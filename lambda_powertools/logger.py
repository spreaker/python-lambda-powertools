import os
import random
import datetime
import traceback
from config import Config
from utils import serialize_log


class Logger:

    def __init__(self):
        self.LEVELS = {
            "DEBUG": 20,
            "INFO": 30,
            "WARN": 40,
            "ERROR": 50,
        }
        self._level = None
        self._context = None
        self.reset()

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Logger, cls).__new__(cls)
        return cls.instance

    def reset(self):
        self._level = self.LEVELS[os.environ.get("LOG_LEVEL", "INFO")]
        self._context = {}

    def set_level(self, level_name):
        self._level = self.LEVELS.get(level_name, self._level)

    def capture(self, env=None, event=None, context=None):
        function_name = None
        function_memory = None
        function_version = None
        aws_request_id = None
        aws_apigw_request_id = None
        aws_cf_request_id = None

        if env is not None:
            function_name = env.get("AWS_LAMBDA_FUNCTION_NAME", None)
            function_memory = int(env.get("AWS_LAMBDA_FUNCTION_MEMORY_SIZE", 0))
            function_version = env.get("AWS_LAMBDA_FUNCTION_VERSION", None)
            if function_version == "$LATEST":
                function_version = None

        if context is not None:
            aws_request_id = context.get("awsRequestId", None)

        if event is not None:
            if event.get("requestContext") and event.get("requestContext").get("apiId"):
                aws_apigw_request_id = event.get("requestContext").get("requestId", None)
            if event.get("headers"):
                aws_cf_request_id = event.get("headers").get("x-amz-cf-id", None)

        self._context = {}
        if function_name is not None:
            self._context["function_name"] = function_name
        if function_version is not None:
            self._context["function_version"] = function_version
        if function_memory is not None:
            self._context["function_memory"] = function_memory
        if aws_request_id is not None:
            self._context["aws_request_id"] = aws_request_id
        if aws_apigw_request_id is not None:
            self._context["aws_apigw_request_id"] = aws_apigw_request_id
        if aws_cf_request_id is not None:
            self._context["aws_cf_request_id"] = aws_cf_request_id

        if event is not None and event.get("headers") and event["headers"].get("x-debug") == "true":
            self.set_level("DEBUG")

    def should_throttle(self, level_name):
        # If the throttle is disabled or the logger is configured in debug level we don't throttle anything
        if not Config.is_log_throttle_enabled() or self._level == self.LEVELS["DEBUG"]:
            return False
        return random.random() > (Config.get_log_throttle(level_name) or 1)

    def log(self, level_name, message, context=None, error=None):
        if self.LEVELS[level_name] < self._level or self.should_throttle(level_name):
            return

        if context is None:
            context = {}

        if isinstance(error, Exception):
            """
            If the error is provided we use the context to pass custom object
            """
            context["error_message"] = str(error)
            context["error_stack"] = "\n".join(traceback.format_exc().splitlines())

        log_str = serialize_log(
            {
                **self._context,
                **(context or {}),
                "time": int(datetime.datetime.now().timestamp() * 1000),
                "loglevel": level_name,
                "message": message,
            }
        )

        print(f"{log_str}\n")

    def debug(self, message, context=None, error=None):
        self.log("DEBUG", message, context, error)

    def info(self, message, context=None, error=None):
        self.log("INFO", message, context, error)

    def warn(self, message, context=None, error=None):
        self.log("WARN", message, context, error)

    def error(self, message, context=None, error=None):
        self.log("ERROR", message, context, error)
