FROM python:3.12.13-alpine3.23

RUN  mkdir -p /workspace/python-lambda-powertools

WORKDIR /workspace/python-lambda-powertools

ADD lambda_powertools ./lambda_powertools
ADD tests ./tests

ADD pyproject.toml ./

RUN pip install ".[dev]" --no-cache-dir