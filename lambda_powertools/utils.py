import json
import math


def parse_bool(value, default_value):
    if type(value) is bool:
        return value
    if type(value) is str:
        value = value.lower()
        return value == "1" or value == "true"
    return default_value


def serialize_log(log):
    response = log.copy()

    for key, value in response.items():
        if value is None:
            response[key] = None
        elif isinstance(value, (str, bool)):
            response[key] = value
        elif isinstance(value, (list, dict)):
            response[key] = json.dumps(value)
        elif math.isnan(value) or (isinstance(value, (int, float)) and not math.isfinite(value)):
            response[key] = None
        else:
            response[key] = value

    return json.dumps(response)
