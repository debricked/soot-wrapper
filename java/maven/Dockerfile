FROM maven:3-jdk-11

COPY common/target/dependency /vulnfunc/java/common/dependency/
COPY common/target/SootWrapper-0.1.jar /vulnfunc/java/common
COPY maven/mavenWrapper.sh /vulnfunc/java/maven/mavenWrapper.sh

CMD /vulnfunc/java/maven/mavenWrapper.sh .
