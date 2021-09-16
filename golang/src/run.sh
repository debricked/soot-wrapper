#!/bin/bash
# Usage: ./run.sh /path/to/package/directory

# utility function used for cleaning up partial files. 
rm_if_exist() {
    if [ -e "$1" ] ; then
        rm $1
    fi
}

# get the script dir to find all files easily
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# ssadump and parse the output
(cd $1 && ssadump -build=F .) | python3 $SCRIPT_DIR/parse_ssadump.py  -o "$SCRIPT_DIR/.parsed_ssadump.json" 

# ast_parse 
all_files=$SCRIPT_DIR/".all_go_files.in"
rm_if_exist $all_files

go_files=($1/*.go)
for go_file in "${go_files[@]}"; do
    abs_path="$(realpath $go_file)"
    echo $abs_path >> $all_files
done

# combine the ast_symbols and ssa_dump and save the final symbols list in "symbol.json"
$SCRIPT_DIR/go_parser < $all_files > "$SCRIPT_DIR/.ast_symbols.json"
python3 $SCRIPT_DIR/combine_ast_ssa.py --parsed_ssadump="$SCRIPT_DIR/.parsed_ssadump.json" --ast_symbols="$SCRIPT_DIR/.ast_symbols.json" -o "$SCRIPT_DIR/symbols.json"

# clean up 
# rm_if_exist "$SCRIPT_DIR/.parsed_ssadump.json"
# rm_if_exist "$SCRIPT_DIR/.ast_symbols.json"
# rm_if_exist $all_files

