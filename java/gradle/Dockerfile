FROM maven:3-jdk-11-slim AS package

COPY java/common /vulnfunc/java/common
RUN mvn -f /vulnfunc/java/common --batch-mode --update-snapshots package

FROM gradle:jre11
RUN apt-get update ; apt-get install --no-install-recommends -y zip
COPY --from=package /vulnfunc/java/common/target/SootWrapper.jar /vulnfunc/java/common/
COPY java/common/*.sh /vulnfunc/java/common/
COPY java/gradle/*.sh /vulnfunc/java/gradle/
