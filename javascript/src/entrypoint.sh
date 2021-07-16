#!/usr/bin/env bash
set -e

# Check if the givet root directory exists
if ! [ -d "$1" ] ; then
    echo "Root project dir not found."
    echo "USAGE: "$0" <rootPackageJsonDir>"
    exit 1
fi

pathToCommonDirectory="/vulnfunc/common"
. $pathToCommonDirectory"/commonWrapper.sh"

# Check that package.json is provided
if ! [ -e "$1/package.json" ] ; then
    echo "package.json not found in $1"
    exit 1
fi

package_dir="${1%/}"

# Check if package-lock.json is provided, this is preferable
# since we then run npm ci instead of npm instal. 
if [ -e "$1/package-lock.json" ] ; then
    npm --prefix $package_dir ci
elif [ -e "$1/yarn.lock"] ; then
    yarn --cwd $package_dir install 
else
    echo "Warning, neither yarn.lock nor package-lock.json was found, proceeding with just package.json"
    npm --prefix $package_dir install
fi

exitIfNotInstalled python3

outputFileName=".debricked-call-graph-javascript"

# Run the actual python script that generates the call graph
echo "Running gen_package_cg"
python3 /vulnfunc/javascript/src/gen_package_cg.py -i $package_dir -o $outputFileName

formatOutput $outputFileName