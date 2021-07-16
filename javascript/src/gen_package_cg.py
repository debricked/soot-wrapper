import glob
import os
import json
import esprima
import re
import glob
import subprocess
import sys
import getopt
from esprima.esprima import parse
from intervaltree import IntervalTree 
from pathlib import Path
import warnings
import demoji
import time

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
   # for subdir in filter(lambda x: os.path.isdir(package_folder + x) and x not in SOURCE_IGNORE, package_dir):
    for subdir in [x for x in package_dir if os.path.isdir(package_folder + x) and x not in SOURCE_IGNORE]:
        js_glob_path = os.path.join(package_folder, subdir, "**/*.js")
        source_code_in_package.extend(glob.glob(js_glob_path, recursive=True))

    # filter out all paths that contain "test" after the package folder
    source_code_in_package = [x for x in source_code_in_package if "test" not in x[len(package_folder):] and Path(x).is_file()]
    return source_code_in_package

 
def gen_cg_for_package(package_folder, output_file):
    start = time.time()
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

    global cg_time; cg_time = 0
    global parse_time; parse_time = 0
    global esprima_time; esprima_time = 0
    

    global cg; cg = {}
    global symbol_ranges_to_footprint; symbol_ranges_to_footprint = {}
    global interval_trees; interval_trees = {}
    global incorrect_syntax_files; incorrect_syntax_files = []
    global dep_graph; dep_graph = {}
    global files_in_packages; files_in_packages = []
    global files_to_dep; files_to_dep = {}
    visited_packages = set()
    parsed_packages = set()

    # recursive function that will be called for each package in the dep-tree
    def rec_gen_cg(rec_package_folder):
       # print("Currently calculating call graph for", rec_package_folder, "and its dependencies.")

        # load dependencies
        try:
            with open(rec_package_folder + 'package.json') as f:
                package_conf = json.load(f)
                dependencies = list(package_conf["dependencies"].keys())
        except (FileNotFoundError, KeyError) as e:
            # package.json is not necesary, but in this case we assume the package has no dependencies
            dependencies = []
        
        # make sure that the current package is not visited again
        visited_packages.add(rec_package_folder) 

        #create an empty set in the dependency graph
        dep_graph[rec_package_folder] = set()

        # add the source files of the current package to 
        source_code_in_curr_package = find_source_files(rec_package_folder)
        files_in_packages.extend(source_code_in_curr_package)
        for script in source_code_in_curr_package:
            files_to_dep[script] = rec_package_folder
    

        # Loop through all dependencies and explore them recursively
        
        for dep in dependencies:

            # find the dependency 
            dep_found = False
    
            # last_checked_for_modules represents where we last looked for node_modules
            last_checked_for_modules = Path(rec_package_folder)
            max_iterations = 1000
            iterations = 0
            while not dep_found:
                # look for node_modules on the different levels
                curr_folder = last_checked_for_modules
                while not (curr_folder / "node_modules").exists() and curr_folder != Path("/"):
                    
                    # this moves the string one step up in the dir tree
                    curr_folder = curr_folder.parent

                # assert that we have found a node_modules directory 
                assert (curr_folder / "node_modules").exists(), "node_modules with " + dep +  " not found for " + rec_package_folder

                # set the next folder to check for the dependency, this is needed if the found 
                # node_modules does not contain our search after package
                last_checked_for_modules = curr_folder.parent

                node_modules = curr_folder / "node_modules"

                # check if the dependency is a single file (very rare but can happen)
                if (node_modules / dep / ".js").exists() and (node_modules / dep / ".js").is_file():
                    dep_found = True
                    files_in_packages.append(str(node_modules / (dep + ".js")))
                    files_to_dep[str(node_modules / (dep + ".js"))] = str(node_modules / (dep + ".js"))
                
                # check if the imported package is a folder
                elif (node_modules / dep).exists():
                    dep_found = True
                    dep_path = str(curr_folder / "node_modules" / dep) + "/"
                    # add the dependency to the dep graph
                    dep_graph[rec_package_folder].add(dep_path)

                    # continue the recursion if the dependency is not already visited
                    if dep_path not in visited_packages:
                        visited_packages.add(dep_path)
                        rec_gen_cg(dep_path)

                iterations += 1
                # break when we have looked in to many node_modules directories. 
                assert iterations < max_iterations, "Dependency not found after " + max_iterations + " searches."
    
    # recursively explore the dependency graph and find the files

    print("Exploring the dependency graphs and finding source files")
    rec_gen_cg(package_folder)

    print("Begin parsing")
    # parse all files
    parse_files()

    # remove all files that weren't parseable
    files_in_packages = [x for x in files_in_packages if x not in incorrect_syntax_files]
  #  print("Files in packages", files_in_packages)
    # generate the call graph
    gen_cg_for_files()

  #  print(cg)

    with open(output_file, "w") as f:
        f.write(json.dumps(cg, indent=4, sort_keys=True))

    end = time.time()
    print("Total time:", end - start)
    print("Parse time:", parse_time, parse_time / (end - start), "% of the total time")
    print("CG time:", cg_time, cg_time / (end - start), "% of the total time")
    print("Esprima time:",esprima_time, esprima_time/parse_time, "% of the total parse time")
    


def parse_files():
    start = time.time()
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
    global parse_time
    global esprima_time
    global files_in_packages

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

            symbol = {"footprint" : footprint, "range" : node.range, "file": file_path}
            # check if we have visited this file before, if not create a new IntervalTree
            if symbol['file'] not in interval_trees:
                interval_trees[symbol['file']] = IntervalTree()
                symbol_ranges_to_footprint[symbol['file']] = {}
            # add the function to the tree
            interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1], symbol)
            symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']

    missing_packagejson_warning_done = False

    even = 0
    # loop through all the files to be parsed and parse them
    for prog_nbr, prog in enumerate(files_in_packages):
        if prog_nbr/len(files_in_packages) > even:
            print(prog_nbr/len(files_in_packages), "% of the files have been parsed")
            even += 0.01

        p = Path(prog)
        p = p.resolve()
        file_path = str(p)
        program_path = str(p)

        package = Path(files_to_dep[prog])
    
        with open(str(package / "package.json"), "r") as f:
            package_json = json.load(f)
        # read the name
        try:
            name = package_json['name']
        except KeyError:
            if not missing_packagejson_warning_done:
                warnings.warn("name not found in package.json for " + str(p) + " using folder name instead")
                missing_packagejson_warning_done = True
            name = p.name
        # remove the first part of the path
        program_path = program_path[len(str(package)):]
        # add the package name instead
        program_path = name + program_path

        # make sure that the files are in unix format
        cmd = ["dos2unix", "-q", prog]
        subprocess.run(cmd, stdout=subprocess.DEVNULL)

        with open(prog, encoding='utf-8') as f:
            program = f.read()

        
        # handle hashbang/shebang by replacing the first line with blank spaces if it starts with #!
        program = re.sub('^#!(.*)', lambda x: len(x.group(0))*" ", program)
        # use esprima to parse the module. When each node is created filter_nodes is called.
        # filter_nodes checks if the node is a function and then stores it in the intervaltree.
        # and in symbol_ranges_to_footprint
        esprima_start = time.time()
        try:
            esprima.parseModule(program, {"loc":True, "range": True}, filter_nodes)
        except esprima.error_handler.Error:
            warnings.warn(prog + " is not correctly written javascript, will ignore it from now on")
            incorrect_syntax_files.append(prog)
            continue
        esprima_end = time.time()

        esprima_time += (esprima_end - esprima_start)

        # add artificial node for the entire script named global
        program_rows = program.split("\n")
        total_number_lines = len(program_rows) + 1
        
        symbol = {"file": file_path, "footprint" : program_path + "/global", "range" : (0, len(program))}
        # check if we have visited this file before, if not create a new IntervalTree
        try:
            if symbol['file'] not in interval_trees:
                interval_trees[symbol['file']] = IntervalTree()
                symbol_ranges_to_footprint[symbol['file']] = {}
            # add the function to the tree
            interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1], symbol)
            symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']
        except ValueError:
            warnings.warn("Unable to add global node to " + symbol['footprint'] + " will ignore it from now on")
            incorrect_syntax_files.append(prog)
    end = time.time()
    parse_time += (end - start)
            

    
def gen_cg_for_files():
    start = time.time()
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
    global cg_time
    global files_in_packages
    global files_to_dep

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
        #print("Target call:", target_call)
        #print("Parsed ranges and footprints:", symbol_ranges_to_footprint)
        # returns the exact function corresponding to the specific target function
        if target_call['file'] == 'Native':
            return 'Native'
        try:
            return symbol_ranges_to_footprint[target_call['file']][(target_call['range']['start'], target_call['range']['end'])]
        except KeyError:
            warnings.warn("Javascript and python has probably parsed " + target_call['file'] + " differently, ignoring the calls to this file")
            return 'Native'


    # if all files are incorrect we should return immidetely, elsewise we will read the old
    # partial_cg.json
    if len(files_in_packages) == 0:
        end = time.time()
        cg_time += (end - start)
        return

    # Call js-callgraph which is an open source static call graph generations tool
    # implementing the approximate call graph algorithm.
    cmd = ["js-callgraph", "--cg"]
    cmd.extend(files_in_packages)
    cmd.extend(["--output", "partial_cg.json"])
    # ignore output 
    subprocess.run(cmd, stdout=subprocess.DEVNULL)

    with open("partial_cg.json", "r") as f:
        partial_cg = json.load(f)

#    print(partial_cg)
    # loop over all the edges found and add them to cg.
    for call in partial_cg:
        # check if the call is from files that we have 
        # check if the call is in the wrong direction, if so, skip it
        
        if call['target']['file'] != 'Native':
            target_in_dep = files_to_dep[call['target']['file']] in dep_graph[files_to_dep[call['source']['file']]]
            same_package = files_to_dep[call['target']['file']] == files_to_dep[call['source']['file']]
            if not target_in_dep and not same_package:
                continue
        source_symbol = symbol_containing_call(call['source'])
        target_symbol = target_search(call['target'])

        if source_symbol not in cg:
            cg[source_symbol] = []
        if target_symbol != "Native" and target_symbol not in cg[source_symbol]:
            cg[source_symbol].append(target_symbol)

    end = time.time()
    cg_time += (end - start)
    
    

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