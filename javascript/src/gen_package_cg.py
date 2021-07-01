import glob
import os
import json
import esprima
import re
import glob
import subprocess
import sys
import getopt
from intervaltree import IntervalTree 


def find_source_files(package_folder):
    """ find_source_files takes a root package folder and returns a list of 
        all .js files not in the dircetories node_modules or test, also all
        paths containing "test" after package_folder are filtered out

    Paramaters:
    package_folder (string): Path to the root package directory

    Returns:
    list[string]: All the found source files ending wih .js
    """
    # ignore folders test and node_modules
    SOURCE_IGNORE = ["test", "node_modules"]
    package_dir = os.listdir(package_folder)

    # add the .js files directly in the main directory
    source_code_in_package = glob.glob(package_folder + "*.js")
    
    # loop through all subdirectories and add all .js files there recursively
    for subdir in filter(lambda x: os.path.isdir(package_folder + x) and x not in SOURCE_IGNORE, package_dir):
        source_code_in_package.extend(glob.glob(package_folder+subdir+"**/*.js", recursive=True))

    # filter out all paths that contain "test" after the package folder
    source_code_in_package = list(filter(lambda x: "test" not in x[len(package_folder):], source_code_in_package))
    return source_code_in_package

 
def gen_cg_for_package(package_folder, output_file):
    """" gen_cg_for_package calculates the call graph for the package in
    package_folder and its dependencies and saves the call graph to
    output_file. The call graph is represented as an adjacency list of
    functions and is saved in json format. 

    Paramaters:
    package_folder (string): Path to the root package directory containing 
    package.json and package-lock.json.

    output_file (string): Path to the output file where the call graph
    is stored. 

    Returns:
    void
    """
    # the rest of the program requires the path to end with / so add it if there isn't any
    if package_folder[-1] != "/":
        package_folder += "/"    

    global cg; cg = {}
    global symbol_ranges_to_footprint; symbol_ranges_to_footprint = {}
    global interval_trees; interval_trees = {}
    global incorrect_syntax_files; incorrect_syntax_files = []
    visited_packages = set()

    # recursive function that will be called for each package in the dep-tree
    def rec_gen_cg(rec_package_folder):

        # load dependencies
        try:
            with open(rec_package_folder + 'package.json') as f:
                package_conf = json.load(f)
                dependencies = list(package_conf["dependencies"].keys())
        except (FileNotFoundError, KeyError) as e:
            # package.json is not necesary, but in this case we assume the package has no 
            dependencies = []

        # find all source code
        source_code_in_curr_package = find_source_files(rec_package_folder)

        # parse all source code files if they have not already been parsed
        if rec_package_folder not in visited_packages:
            parse_files(source_code_in_curr_package)
            visited_packages.add(rec_package_folder)

        # if there are no dependencies we just want to calculate the call graph
        # for package_folder itself
        if len(dependencies) == 0:
            cg_files = source_code_in_curr_package
            # filter away the files not being parsable
            cg_files = list(filter(lambda x: x not in incorrect_syntax_files, cg_files))
            gen_cg_for_files(cg_files, [])

        # Loop through all dependencies and compute the call graph for this package
        # and each of its dependencies. The edges are added to the global variable cg.
        for dep in dependencies:
            dep_found = False
            # last_checked_for_modules represents where we last looked for node_modules
            last_checked_for_modules = rec_package_folder
            max_iterations = 100
            iterations = 0
            while not dep_found:
                # look for node_modules on the different levels
                curr_folder = last_checked_for_modules
                while "node_modules" not in os.listdir(curr_folder) and len(curr_folder) > 1:
                    
                    # this moves the string one step up in the dir tree
                    curr_folder = curr_folder[:(-(curr_folder[:-1][::-1].find("/") + 1))]

                # assert that we have found a node_modules directory 
                assert "node_modules" in os.listdir(curr_folder), "node_modules with " + dep +  " not found for " + rec_package_folder

                # set the next folder to check for the dependency, this is needed if the found 
                # node_modules does not contain our seach after package
                last_checked_for_modules = curr_folder[:(-(curr_folder[:-1][::-1].find("/") + 1))]

                node_modules = os.listdir(curr_folder + "node_modules/")

                # check if the dependency is a single file (very rare but can happen)
                if dep + ".js" in node_modules:

                    dep_found = True
                    parse_files([curr_folder + "node_modules/" + dep + ".js"])
                    cg_files_source = source_code_in_curr_package
                    cg_files_dep = [curr_folder + "node_modules/" + dep + ".js"]
                    cg_files_source = list(filter(lambda x: x not in incorrect_syntax_files, cg_files_source))
                    cg_files_dep = list(filter(lambda x: x not in incorrect_syntax_files, cg_files_dep))
                    gen_cg_for_files(cg_files_source, cg_files_dep)

                # check if the imported package is a folder
                elif dep in node_modules:

                    dep_found = True
                    cg_files_dep = find_source_files(curr_folder + "node_modules/" + dep + "/")
                    parse_files(cg_files_dep)
                    cg_files_source = source_code_in_curr_package
                    cg_files_source = list(filter(lambda x: x not in incorrect_syntax_files, cg_files_source))
                    cg_files_dep = list(filter(lambda x: x not in incorrect_syntax_files, cg_files_dep))
                    gen_cg_for_files(cg_files_source, cg_files_dep)

                    # generate cg recursively for the found package
                    if curr_folder + "node_modules/" + dep + "/" not in visited_packages:
                        visited_packages.add(curr_folder + "node_modules/" + dep + "/")
                        rec_gen_cg(curr_folder + "node_modules/" + dep + "/")
                
                iterations += 1
                # break when we have looked in to many node_modules directories. 
                assert iterations < max_iterations, "Dependency not found after " + max_iterations + " searches."
                
    rec_gen_cg(package_folder)

    with open(output_file, "w") as f:
        f.write(json.dumps(cg, indent=4, sort_keys=True))


def parse_files(script_paths):
    """ parse_files takes a list of files and parses them. The parsing consists of
        finding all functions and saving them in an Interval Tree and the dict
        symbol_ranges_to_footprint. It also saves all uparsable files in 
        incorrect_syntax_files. 

    Paramaters:
    script_paths (list[string]): A list with all the paths to the files to be parsed.

    Returns:
    void
    """
    
    global interval_trees
    global symbol_ranges_to_footprint
    global incorrect_syntax_files

    program_path = ""


    # filter_nodes is called on for every node in the AST. 
    def filter_nodes(node, metadata):
        # check if it is a relevant symbol, if so add it so symbols. 
        if node.type in ["FunctionExpression", "FunctionDeclaration", "ArrowFunctionExpression"]:
            # check if it has a name
            if hasattr(node, "id") and node.id != None:
                name = node.id.name
            else:
                name = "anonymous"
            footprint = program_path + "/" + name + "_from_" + str(node.loc.start.line) + "_to_" + str(node.loc.end.line)

            symbol = {"name": name, "file": program_path, "Line_start": node.loc.start.line, \
            "Line_end" : node.loc.end.line, "type" : node.type, "footprint" : footprint, \
            "start": (node.loc.start.line, node.loc.start.column), "end" : (node.loc.end.line, node.loc.end.column),\
            "range" : node.range}
            # check if we have visited this file before, if not create a new IntervalTree
            if symbol['file'] not in interval_trees:
                interval_trees[symbol['file']] = IntervalTree()
                symbol_ranges_to_footprint[symbol['file']] = {}
            # add the function to the tree
            interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1], symbol)
            symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']

    
    # loop through all the files to be parsed and parse them
    for prog in script_paths:
        program_path = prog
        with open(prog, 'r') as f:
            program = f.read()
        # handle hashbang/shebang by replacing the first line with blank spaces if it starts with #!
        program = re.sub('^#!(.*)', lambda x: len(x.group(0))*" ", program)
        # use esprima to parse the module. When each node is created filter_nodes is called.
        # filter_nodes checks if the node is a function and then stores it in the intervaltree.
        # and in symbol_ranges_to_footprint
        try:
            esprima.parseModule(program, {"loc":True, "range": True}, filter_nodes)
        except esprima.error_handler.Error:
            print("Warning", prog, "is not correctly written javascript, will ignore it from now on")
            incorrect_syntax_files.append(prog)
            continue


        # add artificial node for the entire script named global
        program_rows = program.split("\n")
        total_number_lines = len(program_rows) + 1
        
        symbol = {"name": "global", "file": program_path, "Line_start": 1, \
            "Line_end" : total_number_lines+1, "type" : "global scope", "footprint" : program_path + "/global", \
            "start": (1, 0), "end" : (total_number_lines, len(program_rows[-1])),\
            "range" : (0, len(program))}
        # check if we have visited this file before, if not create a new IntervalTree
        if symbol['file'] not in interval_trees:
            interval_trees[symbol['file']] = IntervalTree()
            symbol_ranges_to_footprint[symbol['file']] = {}
        # add the function to the tree
        interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1], symbol)
        symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']

    
def gen_cg_for_files(source_file_paths, dep_file_paths):
    """ gen_cg_for_files calls js-callgraph with a subprocess and adds the edges to
        the global variable cg.

    Paramaters:
    source_file_paths (list[string]): All the paths to the source code in the 
    soruce package
    
    dep_files_paths (list[string]): All the paths to the source code in the
    dependency package

    Returns:
    void
    """
    global cg 
    global symbol_ranges_to_footprint

    def symbol_containing_call(source_call):
        # returns the symbol that contains the source_call, this is done by taking
        # all functions containing the call and then selecting the smallest one since 
        # this one must be the one directly containing the call
        call_mid_point = (source_call['range']['start'] + source_call['range']['end'])//2

        # pick out all functions containing the call 
        # and pick the smallest interval
        functions_over_call = list(map(lambda x: x.data, interval_trees[source_call['file']][call_mid_point]))
 
        min_covering_function = min(functions_over_call, key = lambda x: x['range'][1] - x['range'][0])

        return min_covering_function['footprint']

    def target_search(target_call):
        # returns the exact function corresponding to the specific target function
        if target_call['file'] == 'Native':
            return 'Native'
        return symbol_ranges_to_footprint[target_call['file']][(target_call['range']['start'], target_call['range']['end'])]

    file_paths = source_file_paths + dep_file_paths

    # Call js-callgraph which is an open source static call graph generations tool
    # implementing the approximate call graph algorithm.
    cmd = ["js-callgraph", "--cg"]
    cmd.extend(file_paths)
    cmd.extend(["--output", "partial_cg.json"])
    # ignore output 
    subprocess.run(cmd, stdout=subprocess.DEVNULL)

    with open("partial_cg.json", "r") as f:
        partial_cg = json.load(f)
    
    # loop over all the edges found and add them to cg.
    for call in partial_cg:
        # check if the call is in the wrong direction, if so, skip it
        if call['target']['file'] in source_file_paths and call['source']['file'] in dep_file_paths:
            continue
        source_symbol = symbol_containing_call(call['source'])
        target_symbol = target_search(call['target'])

        if source_symbol not in cg:
            cg[source_symbol] = []
        if target_symbol != "Native" and target_symbol not in cg[source_symbol]:
            cg[source_symbol].append(target_symbol)
    
    

def main(argv):
    """ main takes command line arguments and runs gen_cg_for_package 
        accordingly.

    Paramaters:
    argv (list[string]) all command line arguments supplied 

    Returns:
    void
    """
    # set default output_file
    output_file = "cg.json"
    input_package = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:")
    except getopt.GetoptError:
        print("gen_package_cg.py -i <input_package> -o <output_file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            input_package = os.path.abspath(arg)
        elif opt == '-o':
            output_file = os.path.abspath(arg)
        elif opt == '-h':
            print("Usage: gen_package_cg.py -i <input_package> -o <output_file>")
    gen_cg_for_package(input_package, output_file)

if __name__ == "__main__":
    main(sys.argv[1:])