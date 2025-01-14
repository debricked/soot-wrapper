FROM maven:3-eclipse-temurin-21-alpine AS package

COPY java/common /vulnfunc/java/common
RUN mvn -f /vulnfunc/java/common --batch-mode --update-snapshots package -DskipTests

FROM maven:3-eclipse-temurin-21-alpine
RUN apk add zip
COPY --from=package /vulnfunc/java/common/target/SootWrapper.jar /vulnfunc/java/common/
COPY java/common/*.sh /vulnfunc/java/common/
COPY java/maven/*.sh /vulnfunc/java/maven/
