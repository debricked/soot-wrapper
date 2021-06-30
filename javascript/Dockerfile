# syntax=docker/dockerfile:1

FROM nikolaik/python-nodejs:python3.8-nodejs14-slim

COPY javascaript/ /vulnfunc/javascript/
RUN pip install -r /vulnfunc/javascript/src/requirements.txt

RUN npm install -g @persper/js-callgraph
