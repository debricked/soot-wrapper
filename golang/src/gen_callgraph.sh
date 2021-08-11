#!/bin/bash
# usage: ./gen_callgraph.sh /input/main/package outputFileName

rm_if_exist() {
    if [ -e "./$1" ] ; then
        rm $1
    fi
}

# get the script dir to find all files easily
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# partial_file1 is used for storing the edges from the pointer analysis
partial_file1="$SCRIPT_DIR/.partial_cg1.out"
# output_file is where the call graph finally is stored
output_file="$SCRIPT_DIR/$2"

echo "Generating edges" 
# change dir to the package directory and run the callgraph command 
(cd $1 && callgraph -format='{{.Caller}} file:{{.Filename}}--->{{.Callee}}' -algo=pta .) \
| sort | uniq > $partial_file1
echo "Done generating edges"

# convert the graph to a nice looking json adjacency list 
echo "Grouping the calls to construct a function -> function call graph"
python3 $SCRIPT_DIR/convert_cg.py -o $output_file < $partial_file1
echo "Call graph generation done"
echo $output_file
# clean up
rm_if_exist $partial_file1