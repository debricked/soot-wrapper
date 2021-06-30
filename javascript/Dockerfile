# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:python3.8-nodejs14-slim

COPY ./src /vulnfunc/javascript/src
RUN chmod +x /vulnfunc/javascript/src/entrypoint.sh

RUN pip install -r /vulnfunc/javascript/src/requirements.txt

RUN npm install -g @persper/js-callgraph

ENTRYPOINT [ "/vulnfunc/javascript/src/entrypoint.sh",  "/vulnfunc/javascript/test/fresh_install"]