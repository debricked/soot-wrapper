#!/usr/bin/env bash
set -e

function exitIfNotInstalled() {
	if [ -z "$2" ] ; then
		name=$1
	else
		name=$2
	fi
	if ! [ `command -v "$1"` > /dev/null 2>&1 ] ; then
		echo $1" command not found. Is "$2" installed?"
		exit 1
	fi
}

exitIfNotInstalled zip
exitIfNotInstalled base64

function formatOutput() {
	if [ -z "$1" ] ; then
		echo "Error: no path specified to formatOutput"
		exit 1
	fi
	echo "Formatting output"
	zip -q $1".zip" $1
	base64 $1".zip" > $1
	rm $1".zip"
}
