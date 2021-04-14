FROM maven:3-jdk-11

COPY java/common/target/dependency /vulnfunc/java/common/dependency/
COPY java/common/target/SootWrapper-0.1.jar /vulnfunc/java/common
COPY java/maven/mavenWrapper.sh /vulnfunc/java/maven/mavenWrapper.sh

CMD /vulnfunc/java/maven/mavenWrapper.sh .
