# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:python3.8-nodejs14-slim
RUN npm install -g @persper/js-callgraph

COPY ./src /vulnfunc/javascript/src
COPY ./test /vulnfunc/javascript/test
RUN chmod +x /vulnfunc/javascript/src/entrypoint.sh

RUN apt-get update ; apt-get install --no-install-recommends -y zip
RUN pip install -r /vulnfunc/javascript/src/requirements.txt

ENTRYPOINT [ "/vulnfunc/javascript/src/entrypoint.sh",  "/vulnfunc/javascript/test/fresh_install"]