#!/usr/bin/env bash
set -e

pathToCommonDirectory="/vulnfunc/java/common"
. $pathToCommonDirectory"/commonWrapper.sh"

exitIfNotInstalled java

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper-0.1-jar-with-dependencies.jar"
outputFileName=".debricked-call-graph"

IFS_bkup=$IFS
IFS=","
userCodeArgs=""
for path in $1
do
	userCodeArgs+="-u \""$path"\" "
done
libraryCodeArgs=""
for path in $2
do
	libraryCodeArgs+="-l \""$path"\" "
done
IFS=$IFS_bkup

echo "Running SootWrapper"
ls -R
echo $pathToSootWrapper $userCodeArgs$libraryCodeArgs-f $outputFileName
java -jar $pathToSootWrapper $userCodeArgs$libraryCodeArgs-f $outputFileName

formatOutput $outputFileName
