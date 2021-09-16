#!/usr/bin/env bash
set -xe

if ! [ -d "$1" ] ; then
	echo "USAGE: "$0" projectRootDirectory"
	exit 1
fi

pathToCommonDirectory="/vulnfunc/common"
. $pathToCommonDirectory"/commonWrapper.sh"

projectRootDirectory="${1%/}"

exitIfNotInstalled mvn maven

cwd=`pwd`
dependencyDir="${cwd%/}/dependencies"
#echo "Copying dependencies to "$dependencyDir" for "$projectRootDirectory
#mvn -q -B -f $projectRootDirectory dependency:copy-dependencies -DoutputDirectory=$dependencyDir --fail-at-end

#echo "Compiling "$projectRootDirectory
#mvn -q -B -f $projectRootDirectory compile --fail-at-end

echo "Compiling and moving dependencies"
mvn -q -B -f $projectRootDirectory package dependency:copy-dependencies -DoutputDirectory=$dependencyDir -DskipTests

pathToSootWrapper=$pathToCommonDirectory"/SootWrapper-0.1-jar-with-dependencies.jar"
outputFileName=".debricked-call-graph-java"
echo "Running SootWrapper"
java -jar $pathToSootWrapper -u $projectRootDirectory"/target/classes" -l $dependencyDir -f $outputFileName

formatOutput $outputFileName
