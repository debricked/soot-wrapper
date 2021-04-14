if ! [ -d "$1" ] ; then
	echo "USAGE: "$0" projectRootDirectory"
	exit 1
fi

projectRootDirectory="${1%/}"

if ! [ `command -v mvn` > /dev/null 2>&1 ] ; then
	echo "mvn command not found. Is maven installed?"
	exit 1
fi

cwd=`pwd`
dependencyDir="${cwd%/}/dependencies"
echo "Copying dependencies to "$dependencyDir" for "$projectRootDirectory
mvn -B -f $projectRootDirectory dependency:copy-dependencies -DoutputDirectory=$dependencyDir --fail-at-end

echo "Compiling "$projectRootDirectory
mvn -B -f $projectRootDirectory compile --fail-at-end

pathToSootWrapper="vulnfunc/java/common/SootWrapper-0.1.jar"
pathToOutputFile=".debricked-call-graph"
echo "Running SootWrapper"
java -jar $pathToSootWrapper -u $projectRootDirectory"/target/classes" -l $dependencyDir -f $pathToOutputFile
