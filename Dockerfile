FROM python:3.9.16-alpine3.17

RUN  mkdir -p /workspace/python-lambda-powertools

WORKDIR /workspace/python-lambda-powertools

COPY requirements-tests.txt ./
RUN pip --no-cache-dir install -r ./requirements-tests.txt

COPY lambda_powertools lambda_powertools
RUN mkdir -p tests
COPY tests/*.py tests/