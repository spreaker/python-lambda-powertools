FROM python:3.9.16-alpine3.17

RUN  mkdir -p /workspace/python-lambda-powertools

WORKDIR /workspace/python-lambda-powertools

ADD lambda_powertools ./lambda_powertools
ADD tests ./tests

ADD setup.py ./

RUN python setup.py pytest