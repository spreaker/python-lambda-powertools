FROM python:3.10.17-alpine3.20

RUN  mkdir -p /workspace/python-lambda-powertools

WORKDIR /workspace/python-lambda-powertools

ADD lambda_powertools ./lambda_powertools
ADD tests ./tests

ADD setup.py ./

RUN pip install . --no-cache-dir