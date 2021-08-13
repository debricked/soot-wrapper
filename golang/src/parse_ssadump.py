import sys
import getopt
import os
import json

def parse_ssadump(output_file):
    """ parse_ssadump reads the output from ssadump from 
    https://pkg.go.dev/golang.org/x/tools though standard in, parses the 
    symbols and saves them in json format in the specified output file.

    Paramaters:
    output_file (string): The path to the output file.

    Returns:
    void 
    """
    symbols = []
    in_symbol = False
    # run ssadump to see an example of how the output looks. 
    for line in sys.stdin:
        if in_symbol and len(line) > 0 and line[0] == "#":
            try:
                format_line = line[2:-1].split()
                symbols[-1][format_line[0][:-1]] = "".join(format_line[1])
            except IndexError:
                continue
        elif in_symbol and len(line) > 0 and line[0] != "#":
            in_symbol = False
        elif not in_symbol and len(line) > 0 and line[0] == "#":
            in_symbol = True
            symbols.append({})
            try:
                format_line = line[2:-1].split()
                symbols[-1][format_line[0][:-1]] = "".join(format_line[1])     
            except IndexError:
                continue

    with open(output_file, "w") as f:
        f.write(json.dumps(symbols, indent=4, sort_keys=True))
    

def main(argv):
    """ main parses the command line arguments (only permit the flag -o)
        and calls the function that converts output from ssadump into
        a symbol list. 

    Paramaters:
    argv (list[string]): the given command line arguments

    Returns:
    void  
    """
    # set default output_file
    output_file = "parsed_ssadump.json"
    input_package = ""
    try:
        opts, args = getopt.getopt(argv, "o:")
    except getopt.GetoptError:
        print("Incorrect usage!")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-o':
            output_file = os.path.abspath(arg)
    parse_ssadump(output_file)

if __name__ == "__main__":
    main(sys.argv[1:])