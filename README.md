# Spreaker Lambda Powertools

Lambda Powertools is a package encapsulating utilities and best practices used to write Python Lambda functions at Spreaker.

## Local development

To develop locally the library spin on the necessary container and run it:

```bash
docker compose up --build

docker compose exec dev sh
```

Then you can run the tests with:

```bash
python setup.py pytest
```

## Releasing

To install the package locally, for inter-project usage, run:

```bash
python setup.py bdist_wheel

pip install ./dist/lambda_powertools-0.1.0-py3-none-any.whl --force-reinstall
```

## Components

### PowerHandler

PowerHandler wraps a traditional Lambda handler and makes it smarter automatically setting up the logger with capturing of environment variables.

Example:

```py
from lambda_powertools.runtime import power_handler

def lambda_body(event, context):
  pass

def lambda_handler(event, context):
  return power_handler(lambda_body)(event, context)
```

### Logger

This logger provides an out-of-the-box logging experience compliant to Spreaker best practices:

- It uses structured logging adhering to the Spreaker logging policies
- When used in conjunction with the PowerHandler it's automatically initialized to capture useful information from the execution environment, like the function version and memory, and the various ids injected by AWS based on the execution context
- It automatically enables debug logging for the incoming requests when specified
- Embedded throttling policy

#### Throttling (optional)

The logger supports throttling that works like this:

- If the log level of the logger is `DEBUG`
    + Logger will log `100%` of `DEBUG`
    + Logger will log `100%` of `INFO`
    + Logger will log `100%` of `WARN`
    + Logger will log `100%` of `ERROR`

- For all the other log levels:
    + Logger will log `0%` of `DEBUG`
    + Logger will log `10%` of `INFO`
    + Logger will log `20%` of `WARN`
    + Logger will log `100%` of `ERROR`

The throttling, disabled by default, can be enabled by setting environment variable `LOG_THROTTLE_ENABLED` to true (`True`, `true`, `1` are all valid values).

#### Example

```py
from lambda_powertools.logger import Logger

logger = Logger()

# Levels
logger.debug("This is debug")
logger.info("This is info")
logger.warn("This is warn")
logger.error("This is error")

# Additional context
logger.info("This is info", { "foo": "bar" })

# Log errors
try:
    raise Exception("Error message")
except Exception as err:
    logger.error("This is error", err)
```
