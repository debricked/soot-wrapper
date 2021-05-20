#!/usr/bin/env bash

sh /vulnfunc/java/gradle/gradleWrapper.sh $1
sh /vulnfunc/java/gradle/removeAction.sh $1
