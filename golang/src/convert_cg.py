import sys
import getopt
import os
import json
from pathlib import Path
import subprocess

def conv_cg(output_file):
    """ conv_cg reads a call graph from standard in on the format 
       {{.Caller}} file:{{.Filename}} {{.Line}} {{.Column}}--->{{.Callee}} from the command
        callgraph from https://pkg.go.dev/golang.org/x/tools, converts 
        into the following format: https://github.com/debricked/vulnerable-functionality/wiki/Output-format
        and saves it as a json. 

    Example of a call graph inputted through standard in:
    debricked.com/go-test-module/hello.Main file:/home/teodor/debricked/vulnerable-functionality/golang/test/hello/hello.go 34 28--->github.com/google/go-github/v36/github.NewClient
    debricked.com/go-test-module/hello.Main file:/home/teodor/debricked/vulnerable-functionality/golang/test/hello/hello.go 36 46--->(*github.com/google/go-github/v36/github.RepositoriesService).ListByOrg
    debricked.com/go-test-module/hello.Main file:/home/teodor/debricked/vulnerable-functionality/golang/test/hello/hello.go 36 65--->context.Background
    debricked.com/go-test-module/hello.Main file:/home/teodor/debricked/vulnerable-functionality/golang/test/hello/hello.go 38 12--->fmt.Print
    debricked.com/go-test-module/hello.Main file:/home/teodor/debricked/vulnerable-functionality/golang/test/hello/hello.go 38 33--->(*github.com/google/go-github/v36/github.Repository).GetFullName

    Parameters:
    output_file (string): the file were the output json-file is saved.

    Returns:
    void
    """

    # these are the packages we will parse later to get better symbol information
    packages_to_parse = set()

    # the adjacency list with all edges reversed. 
    cg = {}
    for inp_line in sys.stdin:
        # split at the "special" charachter "--->"
        line = inp_line.split("--->")
        source_call = line[0].split()
        source = source_call[0]
        call_package_folder = str(Path(source_call[1][5:]).parent)
        packages_to_parse.add(call_package_folder)
        target = line[1][:-1]
        if target not in cg:
            cg[target] = []
        if (source, (int(source_call[2]), int(source_call[3]))) not in cg[target]:
            cg[target].append((source, (int(source_call[2]), int(source_call[3]))))

    # parse the saved packages to get information about the symbols such as position
    # note that we currently only parse the packages where calls are made from
    # since it is rather difficult to obtain the paths to the functions being called

    data_symbols = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # loop thorugh the packages that the calls come from and parse them so that we get information about the symbols
    for package_to_parse in packages_to_parse:
        cmd = [os.path.join(script_dir, "run.sh"), os.path.join(package_to_parse)]
        completed_process = subprocess.run(cmd)

        # if we can parse the package, load the symbols
        if not completed_process.returncode: 
            with open(os.path.join(script_dir, "symbols.json"), "r") as f:
                part_symbols = json.load(f)

            for symbol in part_symbols:
                if 'footprint' in symbol:
                    data_symbols[symbol['footprint']] = symbol

    # convert the reversed adjacancy list into the correct output format by adding the information
    # from the parsed symbols
    list_cg = {}
    list_cg['version'] = 2
    list_cg['data'] = []
    for footprint in cg:
        # if footprint isn't in data_symbols it means that we didn't find when parsing
        if footprint in data_symbols:
            symbol = data_symbols[footprint]
            # TODO: Implement a check for isApplicationClass and isStandardLibraryClass, i.e. the second and third argument in new_element
            new_element = [footprint, False, \
                False, "-", str(Path(symbol['file']).name), symbol['line_start'], symbol['line_end']]
        else:
            new_element = [footprint, False, \
                False, "-", "unknown", "unknown", "unknown"]

        # calless is all the functions calling footprint
        callees = []
        for callee in cg[footprint]:
            callees.append([callee[0], callee[1][0]])
        new_element.append(callees)
        list_cg['data'].append(new_element)


    with open(output_file, "w") as f:
        f.write(json.dumps(list_cg, indent=4, sort_keys=True))
    

def main(argv):
    """ main parses the command line arguments (only permit the flag -o)
        and calls the function that converts the call graph into the 
        proper format and saves it.

    Paramaters:
    argv (list[string]): the given command line arguments

    Returns:
    void  
    """
    # set default output_file
    output_file = "cg.json"
    # parse command line arguments
    try:
        opts, args = getopt.getopt(argv, "o:")
    except getopt.GetoptError:
        print("Incorrect usage!")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-o':
            output_file = os.path.abspath(arg)

    # do what the script is for  
    conv_cg(output_file)

if __name__ == "__main__":
    main(sys.argv[1:])
