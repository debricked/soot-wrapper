# syntax=docker/dockerfile:1

FROM golang:1.16

COPY ./common /vulnfunc/common
COPY ./src /vulnfunc/golang/src

RUN apt-get update ; apt-get install --no-install-recommends -y zip
RUN add-apt-repository ppa:deadsnakes/ppa ; apt-get update ; apt-get install --no-install-recommends -y python3
RUN go get -u golang.org/x/tools/cmd/callgraph

COPY ./entrypoint.sh /vulnfunc/golang/entrypoint.sh
RUN chmod +x /vulnfunc/golang/entrypoint.sh