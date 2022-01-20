#!/usr/bin/env bash
echo "Running vulnerable functionality for Java Maven version 0.3.0"

set -e

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

if ! [ -d "$JAVA_HOME" ] ; then
	unset JAVA_HOME
fi

cwd=`pwd`
dependencyDir="${cwd%/}/dependencies"
echo "Compiling and moving dependencies"
mvn -q -B -f $rootPomDirectory package dependency:copy-dependencies -DoutputDirectory=$dependencyDir -DskipTests

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper.jar"
outputFileName=".debricked-call-graph"
java -jar $pathToSootWrapper $userCodeArgs-l $dependencyDir -f $outputFileName

formatOutput $outputFileName
