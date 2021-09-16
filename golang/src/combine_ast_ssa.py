import json
import getopt
import sys
import os

def combine_ast_ssa(ast_symbols, ssa_dump, output_file):
    """ combine_ast_ssa takes two lists of the same symbols (ast_symbols
    and ssa_dump), combines the information and saves it in the given
    output_file.

    Paramaters:
    ast_symbols (list[dict]): A list of all the symbols from the ast_parser.
    ssa_dump (list[dict]): A list of all the symbols from the ssa build.
    output_file (string): The file where the combined symbols list will 
    be saved. 

    Returns:
    void
    """
    # add easy access to the symbols in ssa_dump through the 'Location'
    ssa_by_location = {}
    for symbol in ssa_dump:
        if 'Location' in symbol and 'Synthetic' not in symbol:
            ssa_by_location[symbol['Location']] = symbol
    
    # For each symbol in ast_symbols add a footprint given by the 
    # ssa_dump 'Name'
    if ast_symbols != None:
        for i in range(len(ast_symbols)):
            Location = ast_symbols[i]['file'] + ":" + ast_symbols[i]['line_start'] + ":" +  ast_symbols[i]['column_start']
            if Location not in ssa_by_location:
                if ast_symbols[i]['file'][-8:] != '_test.go':
                    # print a warning if a symbol was found in the AST-parser
                    # bit not in the ssa build. 
                    print("Warning! " + Location + " not found when building")
            else:
                ast_symbols[i]['footprint'] = ssa_by_location[Location]['Name']
    else:
        ast_symbols = []

    with open(output_file, "w") as f:
        f.write(json.dumps(ast_symbols, indent=4, sort_keys=True))


def main(argv):
    """ main takes command line arguments and calls combine_ast_ssa
    accordingly.

    Paramaters:
    argv (list[string]) all the given command line arguments  

    Returns:
    void
    """    
    try:
        opts, args = getopt.getopt(argv, "ho:", ["parsed_ssadump=", "ast_symbols="])
    except getopt.GetoptError:
        print("combine_ast_ssa.py --parsed_ssadump=<parsed_ssadump_file> --ast_symbols=<parsed_ast_symbols> -o <symbols.json>")
        sys.exit(2)
    
    # set default values
    ast_symbols = {}
    ssa_dump = {}
    output_file = "symbols.json"
    
    # parse the flags
    for opt, arg in opts:
        if opt == '--parsed_ssadump':
            with open(arg, "r") as f:
                ssa_dump = json.load(f)
        elif opt == '--ast_symbols':
            with open(arg, "r") as f:
                ast_symbols = json.load(f)
        elif opt == '-o':
            output_file = os.path.abspath(arg)
        elif opt == '-h':
            print("Usage: combine_ast_ssa.py --parsed_ssadump <parsed_ssadump_file> --ast_symbols <parsed_ast_symbols> -o <symbols.json>")
 
    combine_ast_ssa(ast_symbols, ssa_dump, output_file)

if __name__ == "__main__":
    main(sys.argv[1:])