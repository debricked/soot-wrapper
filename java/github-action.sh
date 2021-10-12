#!/usr/bin/env bash
set -e

pathToCommonDirectory="/vulnfunc/java/common"
. $pathToCommonDirectory"/commonWrapper.sh"

exitIfNotInstalled java

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper-0.1-jar-with-dependencies.jar"
outputFileName=".debricked-call-graph"

echo "Running SootWrapper"
java -jar $pathToSootWrapper -u $1 -l $2 -f $outputFileName

formatOutput $outputFileName
