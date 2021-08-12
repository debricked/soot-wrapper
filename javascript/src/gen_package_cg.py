import glob
import os
import json
import esprima
import re
import subprocess
import sys
import getopt
from intervaltree import IntervalTree 
from pathlib import Path
import warnings
import time
import multiprocessing as mp
import pickle

# for some reason we get recursion limit without this on some small packages
sys.setrecursionlimit(10**6)

def remove_unreachable(starting_nodes, cg):
    """ remove_unreachable takes a call graph and starting nodes and filters
        out the nodes that aren't reachable from the starting nodes

    Paramater:
    starting_nodes (list[string]): the starting nodes in the traversal
    cg (dict): The call graph to be "cleaned"

    Returns:
    dict, the cleaned call graph
    """
    
    starting_nodes = [x for x in starting_nodes if x in cg]
    clean_cg = {}
    vis = set()
    vis.union(starting_nodes)
    que = starting_nodes
    ind = 0

    while ind < len(que):
        curr = que[ind]
        if curr in cg:
            clean_cg[curr] = cg[curr]
            for neigh in cg[curr]:
                if neigh not in vis:
                    vis.add(neigh)
                    que.append(neigh)
        ind += 1
    return clean_cg


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

def slice_data(data, nprocs):
    """ slice_data splits a list in nprocs almost equally long lists.

    Paramaters:
    data (list[]): The list to be partitioned.
    nprocs (int): The number of lists data should be partitioned to.

    Returns:
    list[list[]]: A list with all the partitions. 
    """
    slices = [[] for i in range(nprocs)]
    for i in range(len(data)):
        slices[i % nprocs].append(data[i])
    return slices

def gen_cg_for_package(package_folder, output_file, cg_memory):
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

    cg_memory (int): The target number of bytes to be used in each call 
    to the third party js-callgraph. 

    Returns:
    void
    """
    # the rest of the program requires the path to end with / so add it if there isn't any
    if package_folder[-1] != "/":
        package_folder += "/"    

    global cg_time; cg_time = 0
    global parse_time; parse_time = 0
    global esprima_time; esprima_time = 0
    

    cg = {}
    cg_calls = []
    global symbol_ranges_to_footprint; symbol_ranges_to_footprint = {}
    global interval_trees; interval_trees = {}
    global incorrect_syntax_files; incorrect_syntax_files = []
    global dep_graph; dep_graph = {}
    global files_in_packages; files_in_packages = []
    global files_to_dep; files_to_dep = {}
    global package_to_files; package_to_files = {}
    global time_per_package; time_per_package = {}
    global file_size; file_size = {}
    global space_time; space_time = []
    data_symbols = {}
    visited_packages = set()
    
    # recursive function that will be called for each package in the dep-tree
    def rec_gen_cg(rec_package_folder):
       # print("Currently calculating call graph for", rec_package_folder, "and its dependencies.")

        # make sure that the current package is not visited again
        visited_packages.add(rec_package_folder) 

        #create an empty set in the dependency graph
        dep_graph[rec_package_folder] = set()

        # load dependencies
        try:
            with open(rec_package_folder + 'package.json') as f:
                package_conf = json.load(f)
                dependencies = list(package_conf["dependencies"].keys())
        except (FileNotFoundError, KeyError) as e:
            # package.json is not necesary, but in this case we assume the package has no dependencies
            dependencies = []

        # add the source files of the current package to various global data containers
        source_code_in_curr_package = find_source_files(rec_package_folder)
        files_in_packages.extend(source_code_in_curr_package)
        for script in source_code_in_curr_package:
            files_to_dep[script] = rec_package_folder
            if rec_package_folder not in package_to_files:
                package_to_files[rec_package_folder] = []
            package_to_files[rec_package_folder].append(script)
    

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
                    package_to_files[str(node_modules / (dep + ".js"))] = [str(node_modules / (dep + ".js"))]
                
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

    # parse all files in parallell

    nprocs = mp.cpu_count()
    pool = mp.Pool(processes=nprocs)

    parse_time_start = time.time()

    if os.path.isfile("saved_parse.p") and False:
        parsed = pickle.load( open("saved_parse.p", "rb") )
        interval_trees = parsed['interval_trees']
        symbol_ranges_to_footprint = parsed['symbol_ranges_to_footprint']
        incorrect_syntax_files = parsed['incorrect_syntax_files']
        file_size = parsed['file_size']
    else:
        
        slices = slice_data(files_in_packages, nprocs)
        multi_result = [pool.apply_async(parse_files, (inp, )) for inp in slices]
        for p in multi_result:
            (p_int_tree, p_range_to_symbol, p_incorrect_syntax, p_file_size, p_data_symbols) = p.get()
            interval_trees.update(p_int_tree)
            symbol_ranges_to_footprint.update(p_range_to_symbol)
            incorrect_syntax_files.extend(p_incorrect_syntax)
            file_size.update(p_file_size)
            data_symbols.update(p_data_symbols)

        parsed = {}
        parsed['interval_trees'] = interval_trees
        parsed['symbol_ranges_to_footprint'] = symbol_ranges_to_footprint
        parsed['incorrect_syntax_files'] = incorrect_syntax_files
        parsed['file_size'] = file_size
        pickle.dump( parsed, open("saved_parse.p", "wb") )

    print("Parsing done, beginning to generate call graph")

    parse_time_end = time.time()
    parse_time = parse_time_end - parse_time_start

    # generate the call graph

    pool.close()
    pool.join()    

    pool = mp.Pool(processes=nprocs)

    cg_package_vis = set()

    # cg_memory is the targeted size in bytes for all the files in each js-callgraph run
    cg_memory = 2500000

    # calculate internal cg edges for large projects

    print("Calculating all internal edges")

    for package in package_to_files:
        total_package_memory = 0
        for file in package_to_files[package]:
            if file in file_size:
                total_package_memory += file_size[file]
        if total_package_memory >= cg_memory // 2:
            cg_calls.append(package_to_files[package])
        
        print("Memory for", package, "is", total_package_memory)

    print("Done calculating internal edges")

    def package_visitor(curr_main_package):
        
        print("Currently generating call graph for", curr_main_package, "and its dependencies")

        cg_package_vis.add(curr_main_package)
        deps = list(dep_graph[curr_main_package])

        # dep_files consists of all the files in the direct dependencies

        dep_files = []
        for dep in deps:
            if dep in package_to_files:
                # dep will not be in package_to_files if the package is empty of .js-files
                dep_files.extend(package_to_files[dep])

        dep_files = [x for x in dep_files if x not in incorrect_syntax_files]

        # check if curr_main_package contains any files
        if curr_main_package in package_to_files:
            curr_package_files = package_to_files[curr_main_package]
        else:
            curr_package_files = []

        curr_package_files = [x for x in curr_package_files if x not in incorrect_syntax_files]

        # we can split the current main package curr_memory tracks how much memory we fill
        # for the gen_cg_for_files - call. The strategu consists of filling half that
        # memory with the files from the curr_main_package and half of it with ofther files.
        # This could probably be optimized by analysing the enire dep and main package size.

        curr_memory = 0
        last_path_i = 0
        source_memory = 0
        for path_i, path in enumerate(curr_package_files):
            curr_memory += file_size[path]
            source_memory += file_size[path]
            if curr_memory >= cg_memory // 2 or path_i == len(curr_package_files)-1:
                last_dep_i = 0
                dep_memory = 0
                if len(dep_files) == 0:
                    cg_calls.append(curr_package_files[last_path_i:path_i+1])
                for dep_i, dep_path in enumerate(dep_files):
                    curr_memory += file_size[dep_path]
                    dep_memory += file_size[dep_path]
                    if curr_memory >= cg_memory or dep_i == len(dep_files)-1:
                        cg_calls.append(curr_package_files[last_path_i:path_i+1] + dep_files[last_dep_i:dep_i+1])
                        last_dep_i = dep_i+1
                        curr_memory -= dep_memory
                        dep_memory = 0
                last_path_i = path_i+1
                curr_memory -= source_memory
                curr_memory = 0

        for dep in deps:
            if dep not in cg_package_vis:
                package_visitor(dep)

    # call package_visitor that recursively exploroes the dependency graphs and
    # adds the calls to gen_cg_for_files in the list cg_calls 
    package_visitor(package_folder)

    # run the calls in parallell
    multi_result = [pool.apply_async(gen_cg_for_files, (inp, )) for inp in cg_calls]
    for p_res in multi_result:
        p_cg = p_res.get()
        if p_cg != None:
            # add the results from single calls to cg
            for key in p_cg:
                if key in cg:
                    cg[key] = list(set(cg[key]).union(set(p_cg[key])))
                else:
                    cg[key] = p_cg[key]

    pool.close()
    pool.join()    

    # filter away all the nodes that aren't reachable from the files in package_folder
    # start_nodes = []
    # for source_file in package_to_files[package_folder]:
    #     for func in interval_trees[source_file]:
    #         start_nodes.append(func.data['footprint'])

    # cg = remove_unreachable(start_nodes, cg)

    # format call graph to new format, cg is curently a dict with footprint -> a list of (footprint, (start_row, start_col))
    # where start_row and start_col are where the call is made. Should be formatted to the following format: 
    # https://github.com/debricked/vulnerable-functionality/wiki/Output-format

    list_cg = {}
    list_cg['version'] = 2
    list_cg['data'] = []
    for footprint in cg:
        symbol = data_symbols[footprint]
        new_element = [footprint, files_to_dep[symbol['file']] == package_folder, \
            False, symbol['file_name'], symbol['row_start'], symbol['row_end']]
        callees = []
        for callee in cg[footprint]:
            callees.append([callee[0], callee[1][0]])
        new_element.append(callees)
        list_cg['data'].append(new_element)

    with open(output_file, "w") as f:
        f.write(json.dumps(list_cg, indent=4, sort_keys=True))

    end = time.time()

    for partial_cg in glob.glob("partial_cg*.json"):
        os.remove(partial_cg)

    print("Total time:", end - start)
    print("Parse time:", parse_time, parse_time / (end - start) * 100, "% of the total time")


def parse_files(source_files):
  
    """ parse_files takes a list of files and parses them. The parsing consists of
        finding all functions and saving them in an Interval Tree and the dict
        symbol_ranges_to_footprint. It also saves all unparsable files in 
        incorrect_syntax_files and adds an artificial "global" ast node. 

    Paramaters:
    source_files (list[string]): A list with all the paths to the files to be parsed.

    Returns:
    (dict, dict, list[string], dict)

    string -> IntervalTree dict where an IntervalTree is stored
    for each file.

    string -> (int, int) -> string dict that saves
    the symbol footprints for each file and range (i.e. the column if the entire
    file was written on a single row).

    a list with all the files that caused parsing errors.

    string -> int dict that saves the number of bytes each file occupates. 
    """

    interval_trees = {}
    symbol_ranges_to_footprint = {}
    incorrect_syntax_files = []
    file_size = {}
    data_symbols = {}

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

            footprint = program_path + "/" + name + "_at_" + str(node.loc.start.line) + ":" + str(node.loc.start.column)

            symbol = {"footprint" : footprint, "range" : node.range, "file": file_path}

            data_symbol = {"footprint" : footprint, "range" : node.range, "file_name": Path(file_path).name, \
                "row_start": node.loc.start.line, "row_end": node.loc.end.line, "file": file_path}

            # check if we have visited this file before, if not create a new IntervalTree
            if symbol['file'] not in interval_trees:
                interval_trees[symbol['file']] = IntervalTree()
                symbol_ranges_to_footprint[symbol['file']] = {}
            # add the function to the tree, we use symbol['range'][1]+1 in since the intervals are
            # non inclusive at the right limit, but inclusive for the left limit. So when we query
            # the interval tree it is as though we have inclusion at both ends. 
            interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1]+1, symbol)
            symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']
            data_symbols[data_symbol['footprint']] = data_symbol

    # loop through all the files to be parsed and parse them
    for prog_nbr, prog in enumerate(source_files):

        p = Path(prog)
        p = p.resolve()
        file_path = str(p)
        program_path = str(p)

        package = Path(files_to_dep[prog])
        try:
            with open(str(package / "package.json"), "r") as f:
                package_json = json.load(f)
                name = package_json['name']
        except (FileNotFoundError, KeyError) as e:
          #  if not missing_packagejson_warning_done:
            warnings.warn("package-json not found or name not found in package.json for " + str(p) + " using folder name instead")
            #    missing_packagejson_warning_done = True
            name = package.name
  
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
        try:
            esprima.parseModule(program, {"loc":True, "range": True}, filter_nodes)
        except esprima.error_handler.Error:
            warnings.warn("Parser is not able to parse " + prog + ", will ignore it from now on")
            incorrect_syntax_files.append(prog)
            continue

        # add artificial node for the entire script named global
        
        symbol = {"file": file_path, "footprint" : program_path + "/global", "range" : (0, len(program))}

        # data_symbol is a bigger symbol containing all the function data
        data_symbol = {"file_name": Path(file_path).name, "footprint" : program_path + "/global", "range" : (0, len(program)), \
            "row_start": 0, "row_end": len(prog.split("\n"))+1, "file": file_path}
        
        # check if we have visited this file before, if not create a new IntervalTree
        try:
            if symbol['file'] not in interval_trees:
                interval_trees[symbol['file']] = IntervalTree()
                symbol_ranges_to_footprint[symbol['file']] = {}
            # add the function to the tree
            interval_trees[symbol['file']].addi(symbol['range'][0], symbol['range'][1]+1, symbol)
            symbol_ranges_to_footprint[symbol['file']][tuple(symbol['range'])] = symbol['footprint']
            # add the function to the data_dict
            data_symbols[data_symbol['footprint']] = data_symbol
        except ValueError:
            warnings.warn("Unable to add global node to " + symbol['footprint'] + " will ignore it from now on")
            incorrect_syntax_files.append(prog)
            continue

        p = Path(prog)
        p = p.resolve()
        file_size[prog] = p.stat().st_size
    
    return (interval_trees, symbol_ranges_to_footprint, incorrect_syntax_files, file_size, data_symbols)
    
def gen_cg_for_files(all_cg_files):
    """ gen_cg_for_files calls js-callgraph with a subprocess and returns
    the edges. 

    Paramaters:
    all_cg_files (list[string]): All the paths to the source code 

    Returns:
    cg (dict): A string -> list[string] dict that saved the edges in an
    adjecency list form. 
    """
    cg  = {}
    global symbol_ranges_to_footprint
    global cg_time
    global files_to_dep
    global interval_trees
    global incorrect_syntax_files
    global file_size

    def symbol_containing_call(source_call):
        # returns the symbol that contains the source_call, this is done by taking
        # all functions containing the call and then selecting the smallest one since 
        # this one must be the one directly containing the call

        # pick out all functions containing the call by intersecting all intervals
        # containing the the start and end of the call and pick the smallest interval
        functions_over_call = list(map(lambda x: x.data, \
            interval_trees[source_call['file']][source_call['range']['start']] & \
            interval_trees[source_call['file']][source_call['range']['end']]))
 
        min_covering_function = min(functions_over_call, key = lambda x: x['range'][1] - x['range'][0])

        return min_covering_function['footprint']

    def target_search(target_call):
        # returns the exact function corresponding to the specific target function
        
        if target_call['file'] == 'Native':
            return 'Native'
        try:
            return symbol_ranges_to_footprint[target_call['file']][(target_call['range']['start'], target_call['range']['end'])]
        except KeyError:
            warnings.warn("Javascript and python has probably parsed " + target_call['file'] + " differently, ignoring the calls to this file")
            return 'Native'

    
    all_cg_files = [x for x in all_cg_files if x not in incorrect_syntax_files]

    # print the total memory used in the js-callgraph call
    tot_memory = 0
    for file in all_cg_files:
        tot_memory += file_size[file]
    print("Total memory for the cg run:", tot_memory / 1000, "kB")

    # if all files are incorrect we should return immediately, elsewise we will read the old
    # partial_cg.json
    if len(all_cg_files) == 0:
        return

    # Call js-callgraph which is an open source static call graph generations tool
    # implementing the approximate call graph algorithm.
    cmd = ["js-callgraph", "--cg"]
    cmd.extend(all_cg_files)
    cmd.extend(["--output", "partial_cg_" + str(os.getpid()) + ".json"])

    print("Starting node cg process...")

    print("Number of files:", len(all_cg_files))

    completed_process = subprocess.run(cmd, stdout=subprocess.DEVNULL)
 
    print("Done with node cg process...")

    if not completed_process.returncode: 
        with open("partial_cg_" + str(os.getpid()) + ".json", "r") as f:
            partial_cg = json.load(f)
    else:
        # return None if the call graph generation failed
        return None

    # loop over all the edges found and add them to cg.
    for call in partial_cg:
        # check if the call is in the wrong direction, if so, skip it
        try:
            if call['target']['file'] != 'Native':
                target_in_dep = files_to_dep[call['target']['file']] in dep_graph[files_to_dep[call['source']['file']]]
                same_package = files_to_dep[call['target']['file']] == files_to_dep[call['source']['file']]
                if not target_in_dep and not same_package:
                    continue
            source_symbol = symbol_containing_call(call['source'])
            target_symbol = target_search(call['target'])

            if target_symbol != "Native" and target_symbol not in cg:
                cg[target_symbol] = []
            if target_symbol != "Native" and (source_symbol, (call['source']['start']['row'], call['source']['start']['column'])) not in cg[target_symbol]:
                cg[target_symbol].append((source_symbol, (call['source']['start']['row'], call['source']['start']['column'])))
        except ValueError:
            warnings.warn("Was not able to find enclosing function for \n" + str(call) + "\n ignoring this call. The underlaying reason is probably that python and javascript have parsed it differently.")

    return cg
    
    

def main(argv):
    """ main takes command line arguments and runs gen_cg_for_package 
        accordingly.

    Paramaters:
    argv (list[string]) all command line arguments supplied 

    Returns:
    void
    """
    # set default values
    output_file = "cg.json"
    input_package = ""
    cg_memory = 2500000
    try:
        opts, args = getopt.getopt(argv, "hi:o:m:")
    except getopt.GetoptError:
        print("gen_package_cg.py -i <input_package> -o <output_file> -m <memory_for_each_run>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            input_package = os.path.abspath(arg)
        elif opt == '-o':
            output_file = os.path.abspath(arg)
        elif opt == '-m':
            cg_memory = int(arg)
        elif opt == '-h':
            print("Usage: gen_package_cg.py -i <input_package> -o <output_file> -m <memory_for_each_run>")
    gen_cg_for_package(input_package, output_file, cg_memory)

if __name__ == "__main__":
    main(sys.argv[1:])
