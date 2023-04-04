import os
import json
import builtins
import datetime
import pytest
from unittest import mock
from lambda_powertools.runtime import power_handler
from lambda_powertools.logger import logger

MOCK_DATE_MS = 1679313252.708


@pytest.fixture(autouse=True)
def patch_datetime_now(monkeypatch):
    class MyDateTime:
        @classmethod
        def now(cls):
            return MyDateTime()

        def timestamp(self):
            return MOCK_DATE_MS

    monkeypatch.setattr(datetime, 'datetime', MyDateTime)


@mock.patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "lambda-powertools-runtime"})
@mock.patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_VERSION": "1"})
@mock.patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128"})
def test_power_handler_initialize_the_logger_to_properly_capture_context(mocker):
    print_spy = mocker.spy(builtins, "print")

    def lambda_body(event, context):
        logger.info("this is a log", {"foo": "bar"})
        return {"foo": "bar"}

    response = power_handler(lambda_body)(
        {
            "requestContext": {"apiId": "_", "requestId": "apiGwRequestId"},
            "headers": {"x-amz-cf-id": "cfRequestId"}
        },
        # context is a LambdaContext object, not a dict
        context=type('', (object,), {"aws_request_id": "awsRequestId"})()
    )

    assert response == {"foo": "bar"}
    print_spy.assert_called_once()
    print_spy.assert_called_with("{}\n".format(json.dumps({
        # From environment
        "function_name": "lambda-powertools-runtime",
        "function_version": "1",
        "function_memory": 128,
        # From context
        "aws_request_id": "awsRequestId",
        # From event
        "aws_apigw_request_id": "apiGwRequestId",
        "aws_cf_request_id": "cfRequestId",
        # Other
        "foo": "bar",
        "time": 1679313252708,
        "loglevel": "INFO",
        "message": "this is a log"
    })))
