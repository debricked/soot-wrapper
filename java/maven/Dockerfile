FROM maven:3-jdk-11

COPY java/common /vulnfunc/java/common
RUN mvn -f /vulnfunc/java/common --batch-mode --update-snapshots package
COPY java/maven/mavenWrapper.sh /vulnfunc/java/maven/mavenWrapper.sh

CMD /vulnfunc/java/maven/mavenWrapper.sh .
