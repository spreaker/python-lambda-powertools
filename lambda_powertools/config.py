import os
from lambda_powertools.utils import parse_bool


class Config:
    LOG_THROTTLE = {
        "INFO": 0.1,  # 10%
        "WARN": 0.2  # 20%
    }

    @classmethod
    def is_log_throttle_enabled(cls):
        return parse_bool(os.environ.get("LOG_THROTTLE_ENABLED"), False)

    @classmethod
    def get_log_throttle(cls, level_name):
        return cls.LOG_THROTTLE.get(level_name)
