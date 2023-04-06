import os
import lambda_powertools.prometheus as prometheus
from lambda_powertools.logger import logger


def power_handler(wrapped_handler):

    def wrapper(event, context):
        logger.reset()
        logger.capture(env=os.environ, event=event, context=context)

        prometheus.reset()

        response = None
        error = None
        try:
            response = wrapped_handler(event, context)
        except Exception as e:
            error = e

        prometheus.flush_metrics()

        if error is not None:
            raise error

        return response

    return wrapper
