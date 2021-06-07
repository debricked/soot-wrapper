#!/usr/bin/env bash
set -e

if ! [ -d "$1" ] ; then
	echo "USAGE: "$0" projectRootDirectory"
	exit 1
fi

projectRootDirectory="${1%/}"

if ! [ `command -v gradle` > /dev/null 2>&1 ] ; then
	echo "gradle command not found. Is gradle installed?"
	exit 1
fi

cwd=`pwd`
cd $projectRootDirectory
if ! [ -f "build.gradle" ] ; then
	echo "no build.gradle found in "$projectRootDirectory
	exit 1
fi

dependencyDir="${cwd%/}/dependencies"
taskName="__debricked_vulnerable_functionality"
if ! grep -q "$taskName" "build.gradle" ; then
	echo "Appending task to build.gradle"
	printf '\nallprojects{\n\ttask %s(type: Copy) {\n\t\tinto "%s"\n\t\tfrom configurations.default\n\t}\n}\n' "$taskName" "$dependencyDir" >> build.gradle
fi

echo "Copying dependencies to "$dependencyDir" for "$projectRootDirectory
gradle -q $taskName

echo "Compiling "$projectRootDirectory
gradle -q compileJava

cd $cwd
#pathToSootWrapper="/vulnfunc/java/common/target/SootWrapper-0.1.jar"
pathToSootWrapper="./java/common/target/SootWrapper-0.1-jar-with-dependencies.jar"
pathToOutputFile=".debricked-call-graph"
echo "Running SootWrapper"
java -jar $pathToSootWrapper -u $projectRootDirectory"/build/classes/java/main" -l $dependencyDir -f $pathToOutputFile

echo "Formatting output"
zip -q $pathToOutputFile".zip" $pathToOutputFile
base64 $pathToOutputFile".zip" > $pathToOutputFile
rm $pathToOutputFile".zip"
