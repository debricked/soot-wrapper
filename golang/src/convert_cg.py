import sys
import getopt
import os
import json

def conv_cg(output_file):
    """ conv_cg reads a call graph from standard in on the format 
        {{.Caller}} file:{{.Filename}}--->{{.Callee}} from the command
        callgraph from https://pkg.go.dev/golang.org/x/tools, converts 
        into a adjacency list and saves it in json format. 

    Parameters:
    output_file (string): the file were the output json-file is saved.

    Returns:
    void
    """
    # the adjacency list with all edges. 
    cg = {}
    for inp_line in sys.stdin:
        # split att the "special" charachter "--->"
        line = inp_line.split("--->")
        source = line[0].split()[0]
        target = line[1][:-1]
        if source not in cg:
            cg[source] = []
        if target not in cg[source]:
            cg[source].append(target)
    
    with open(output_file, "w") as f:
        f.write(json.dumps(cg, indent=4, sort_keys=True))
    

def main(argv):
    """ main parses the command line arguments (only permit the flag -o)
        and calls the function that converts the call graph into an
        adjacency list and saves it.

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
