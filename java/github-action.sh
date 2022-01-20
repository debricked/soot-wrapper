#!/usr/bin/env bash
echo "Running vulnerable functionality for Java (generic) version 0.3.0"

set -e

pathToCommonDirectory="/vulnfunc/java/common"
. $pathToCommonDirectory"/commonWrapper.sh"

exitIfNotInstalled java

IFS_bkup=$IFS
IFS=","
userCodeArgs=""
for path in $1
do
	userCodeArgs+="-u "$path" "
done
libraryCodeArgs=""
for path in $2
do
	libraryCodeArgs+="-l "$path" "
done
IFS=$IFS_bkup

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper.jar"
outputFileName=".debricked-call-graph"
java -jar $pathToSootWrapper $userCodeArgs$libraryCodeArgs-f $outputFileName

formatOutput $outputFileName
