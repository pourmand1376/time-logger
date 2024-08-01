# Time Logger

This project provides a simple way to profile the execution time of your Python functions.

## Features

- Measure the execution time of functions with the `@profiling` decorator.
- Optionally log the start and end times of function execution.
- Log specific variables or all arguments passed to the function.
- Choose between using the standard `print` function or a custom logger for output.

## Installation

```bash
pip install -e .
```

## Usage

```python
from time_logger import profiling

# Basic usage
@profiling()
def my_function():
    # Your code here

# Log start and end times
@profiling(log_start=True)
def my_function():
    # Your code here

# Log specific variables
@profiling(log_variables=['my_variable'])
def my_function(my_variable):
    # Your code here

# Log all arguments
@profiling(log_all_args=True)
def my_function(arg1, arg2):
    # Your code here

# Use a custom logger
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)

@profiling(logger=logger)
def my_function():
    # Your code here
```

## Examples

See the `tests/test_profiling.py` file for more examples.
