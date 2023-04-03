import os
from lambda_powertools.logger import logger


def power_handler(wrapped_handler):

    def wrapper(event, context):
        logger.reset()
        logger.capture(env=os.environ, event=event, context=context)

        response = None
        error = None
        try:
            response = wrapped_handler(event, context)
        except Exception as e:
            error = e

        if error is not None:
            raise error

        return response

    return wrapper
