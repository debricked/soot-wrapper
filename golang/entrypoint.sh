#!/usr/bin/env bash
set -e

# Check if the givet root directory exists
if ! [ -d "$1" ] ; then
    echo "Root project dir not found."
    echo "USAGE: "$0" <rootGoModDir>"
    exit 1
fi

pathToCommonDirectory="/vulnfunc/common"
. $pathToCommonDirectory"/commonWrapper.sh"

# Check that package.json is provided
if ! [ -e "$1/go.mod" ] ; then
    echo "go.mod not found in $1"
    exit 1
fi

module_dir="${1%/}"
module_dir=dirname "$(realpath $module_dir/go.mod)"
echo $module_dir
echo $PWD
# install dependencies
cd $module_dir && go install

exitIfNotInstalled python3

exitIfNotInstalled go

outputFileName=".debricked-call-graph-golang"

# Run the actual script that generates the call graph
echo "Running call graph generator"
/vulnfunc/golang/src/gen_callgraph.sh "$module_dir" $outputFileName

cat "/vulnfunc/golang/src/$outputFileName"

formatOutput "/vulnfunc/golang/src/$outputFileName"