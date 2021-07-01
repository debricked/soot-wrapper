#!/usr/bin/env bash
set -e

 
# The follwing functions are taken from commonWrapper.sh
exitIfNotInstalled() {
	if [ -z "$2" ] ; then
		name=$1
	else
		name=$2
	fi
	if ! [ `command -v "$1"` > /dev/null 2>&1 ] ; then
		echo $1" command not found. Is "$name" installed?"
		exit 1
	fi
}

exitIfNotInstalled zip
exitIfNotInstalled base64

formatOutput() {
	if [ -z "$1" ] ; then
		echo "Error: no path specified to formatOutput"
		exit 1
	fi
	echo "Formatting output"
	zip -q $1".zip" $1
	base64 $1".zip" > $1
	rm $1".zip"
}

# Check if the givet root directory exists
if ! [ -d "$1" ] ; then
    echo "Root project dir not found."
    echo "USAGE: "$0" <rootPackageJsonDir>"
    exit 1
fi

# Check that package.json is provided
if ! [ -e "$1/package.json" ] ; then
    echo "package.json not found in $1"
    exit 1
fi

package_dir="${1%/}"

# Check if package-lock.json is provided, this is preferable
# since we then run npm ci instead of npm instal. 
if ! [ -e "$1/package-lock.json" ] ; then
    echo "Warning, package-lock.json is missing, proceding with only package.json"
    npm --prefix $package_dir install
else
    npm --prefix $package_dir ci
fi 

exitIfNotInstalled python3

outputFileName=".debricked-call-graph"

# Run the actual python script that generates the call graph
echo "Running gen_package_cg"
python3 /vulnfunc/javascript/src/gen_package_cg.py -i $package_dir -o $outputFileName

formatOutput $outputFileName