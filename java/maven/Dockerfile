FROM maven:3-jdk-11-slim AS package

COPY java/common /vulnfunc/java/common
RUN mvn -f /vulnfunc/java/common --batch-mode --update-snapshots package

FROM maven:3-jdk-11-slim
COPY --from=package /vulnfunc/java/common/target/SootWrapper-0.1-jar-with-dependencies.jar /vulnfunc/java/common/target/SootWrapper-0.1.jar
COPY java/maven/*.sh /vulnfunc/java/maven/
