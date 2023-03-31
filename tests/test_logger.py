import pytest
import os
import builtins
import datetime
import json
from unittest import mock
from lambda_powertools.logger import Logger
from lambda_powertools.config import Config

MOCK_DATE_MS = 1679313252.708


@pytest.fixture(autouse=True)
def mock_before_each():
    with mock.patch.dict(
            os.environ,
            {"LOG_THROTTLE_ENABLED": "false"}
    ):
        yield


@pytest.fixture(autouse=True)
def patch_datetime_now(monkeypatch):
    class MyDateTime:
        @classmethod
        def now(cls):
            return MyDateTime()

        def timestamp(self):
            return MOCK_DATE_MS

    monkeypatch.setattr(datetime, 'datetime', MyDateTime)


@pytest.fixture(scope='function')
def debug_logger():
    logger = Logger()
    logger.reset()
    logger.set_level("DEBUG")
    return logger


@pytest.fixture(scope='function')
def info_logger():
    logger = Logger()
    logger.reset()
    logger.set_level("INFO")
    return logger


@pytest.fixture(scope='function')
def warn_logger():
    logger = Logger()
    logger.reset()
    logger.set_level("WARN")
    return logger


@pytest.fixture(scope='function')
def error_logger():
    logger = Logger()
    logger.reset()
    logger.set_level("ERROR")
    return logger


def test_debug_logger_should_respect_log_level(debug_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    debug_logger.set_level("INFO")
    debug_logger.debug("boo")
    print_spy.assert_not_called()


def test_debug_logger_should_log_the_message(debug_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    debug_logger.debug("boo")
    print_spy.assert_called_once()
    print_spy.assert_called_with('{"time": 1679313252708, "loglevel": "DEBUG", "message": "boo"}\n')


def test_warn_logger_should_respect_log_level(warn_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    warn_logger.set_level("ERROR")
    warn_logger.debug("boo")
    print_spy.assert_not_called()


def test_warn_logger_should_log_the_message(warn_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    warn_logger.warn("boo")
    print_spy.assert_called_once()
    print_spy.assert_called_with('{"time": 1679313252708, "loglevel": "WARN", "message": "boo"}\n')


def test_error_logger_should_log_the_message(error_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    error_logger.error("boo")
    print_spy.assert_called_once()
    print_spy.assert_called_with('{"time": 1679313252708, "loglevel": "ERROR", "message": "boo"}\n')


def test_capture_should_activate_debug_logs(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    info_logger.capture(event={"headers": {"x-debug": "true"}})
    info_logger.debug("boo")
    print_spy.assert_called_once()
    print_spy.assert_called_with('{"time": 1679313252708, "loglevel": "DEBUG", "message": "boo"}\n')


def test_capture_should_capture_information_and_add_them(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    info_logger.capture(
        env={
            "AWS_LAMBDA_FUNCTION_NAME": "lambda-powertools",
            "AWS_LAMBDA_FUNCTION_VERSION": "1",
            "AWS_LAMBDA_FUNCTION_MEMORY_SIZE": "128"
        },
        event={
            "requestContext": {"apiId": "_", "requestId": "apiGwRequestId"},
            "headers": {"x-amz-cf-id": "cfRequestId"}
        },
        context={
            "awsRequestId": "awsRequestId"
        }
    )
    info_logger.info("boo")

    print_spy.assert_called_once()
    print_spy.assert_called_with("{}\n".format(json.dumps({
        # From environment
        "function_name": "lambda-powertools",
        "function_version": "1",
        "function_memory": 128,
        # From context
        "aws_request_id": "awsRequestId",
        # From event
        "aws_apigw_request_id": "apiGwRequestId",
        "aws_cf_request_id": "cfRequestId",
        # Other
        "time": 1679313252708,
        "loglevel": "INFO",
        "message": "boo"
    })))


def test_provided_context_is_printed_with_the_log(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    info_logger.info("boo", {"foo": "bar"})

    print_spy.assert_called_once()
    print_spy.assert_called_with("{}\n".format(json.dumps({
        # From context
        "foo": "bar",
        # Other
        "time": 1679313252708,
        "loglevel": "INFO",
        "message": "boo"
    })))


def test_provided_error_is_printed_with_the_log(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    info_logger.info("boo", error=Exception("bar"))

    print_spy.assert_called_once()
    print_spy.assert_called_with("{}\n".format(json.dumps({
        # From error
        "error_message": "bar",
        "error_stack": "NoneType: None",
        # Other
        "time": 1679313252708,
        "loglevel": "INFO",
        "message": "boo"
    })))


def test_provided_context_and_error_are_printed_with_the_log(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")

    info_logger.info(
        "boo",
        context={"foo": {"bar": {"baz": "foobarbaz"}}},
        error=Exception("bar")
    )

    print_spy.assert_called_once()
    print_spy.assert_called_with("{}\n".format(json.dumps({
        # From context
        "foo": '{"bar": {"baz": "foobarbaz"}}',
        # From error
        "error_message": "bar",
        "error_stack": "NoneType: None",
        # Other
        "time": 1679313252708,
        "loglevel": "INFO",
        "message": "boo"
    })))


@mock.patch.dict(os.environ, {"LOG_THROTTLE_ENABLED": "true"})
def test_not_all_messages_should_be_logged_with_throttling_enabled(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")
    Config.LOG_THROTTLE = {"INFO": 0.1}

    info_logger.info("1")
    info_logger.info("2")
    info_logger.info("3")
    info_logger.info("4")
    info_logger.info("5")
    info_logger.info("6")
    info_logger.info("7")
    info_logger.info("8")
    info_logger.info("9")
    info_logger.info("10")

    assert print_spy.call_count < 10


@mock.patch.dict(os.environ, {"LOG_THROTTLE_ENABLED": "false"})
def test_all_messages_should_be_logged_with_throttling_disabled(info_logger, mocker):
    print_spy = mocker.spy(builtins, "print")
    Config.LOG_THROTTLE = {"INFO": 0.1}

    info_logger.info("1")
    info_logger.info("2")
    info_logger.info("3")
    info_logger.info("4")
    info_logger.info("5")
    info_logger.info("6")
    info_logger.info("7")
    info_logger.info("8")
    info_logger.info("9")
    info_logger.info("10")

    assert print_spy.call_count == 10
