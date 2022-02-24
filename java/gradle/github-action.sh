#!/usr/bin/env bash

echo "Running vulnerable functionality for Java Gradle version 0.4.1"

sh /vulnfunc/java/gradle/gradleWrapper.sh $1
sh /vulnfunc/java/gradle/removeAction.sh $1
