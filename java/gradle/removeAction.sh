#!/usr/bin/env bash
set -e

if ! [ -d "$1" ] ; then
	echo "USAGE: "$0" projectRootDirectory"
	exit 1
fi

fileName="${1%/}/build.gradle"
taskName="__debricked_vulnerable_functionality"
if grep -q "$taskName" "$fileName"  ; then
	echo "Removing task from build.gradle"
	head -n -7 $fileName > $fileName".tmp"
	mv -f $fileName".tmp" $fileName
fi
