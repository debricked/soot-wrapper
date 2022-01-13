#!/usr/bin/env bash
env

set -xe

pathToCommonDirectory="/vulnfunc/java/common"
. $pathToCommonDirectory"/commonWrapper.sh"

exitIfNotInstalled mvn maven
exitIfNotInstalled java

#rootPomDirectory is the folder that contains your root pom.xml file
if ! [ -d "$1" ] ; then
	echo "USAGE: "$0" rootPomDirectory [pathToCompiledFiles]"
	exit 1
fi
rootPomDirectory="${1%/}"

IFS_bkup=$IFS
IFS=","
userCodeArgs=""
for path in $2
do
	userCodeArgs+="-u "$rootPomDirectory"/"$path" "
done
IFS=$IFS_bkup

cwd=`pwd`
dependencyDir="${cwd%/}/dependencies"
echo "Compiling and moving dependencies"
mvn -q -B -f $rootPomDirectory package dependency:copy-dependencies -DoutputDirectory=$dependencyDir -DskipTests

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper-0.1-jar-with-dependencies.jar"
outputFileName=".debricked-call-graph"
echo "Running SootWrapper"
java -jar $pathToSootWrapper $userCodeArgs-l $dependencyDir -f $outputFileName

formatOutput $outputFileName
