FROM python:3.14-alpine

RUN  mkdir -p /workspace/python-lambda-powertools

WORKDIR /workspace/python-lambda-powertools

COPY lambda_powertools ./lambda_powertools
COPY tests ./tests

COPY pyproject.toml ./

RUN pip install ".[dev]" --no-cache-dir