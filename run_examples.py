import logging

from src.time_logger import profiling

import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)


@profiling(log_start=True, log_variables=["time"], logger=logger)
def run_400(time=200):
    for i in range(time):
        i *= i


@profiling(log_start=False)
def run_500(time=200):
    for i in range(time):
        i *= i


@profiling(logger=logger, log_variables=["args"], log_start=True)
def sum(*args):
    total = 0
    for i in args:
        total += i
    return total


@profiling(log_all_args=True, log_start=True)
def multiply(a, b, c=1):
    return a * b * c

@profiling(
    custom_message="Processing order {order_id} for customer {customer_name}"
)
def process_order(order_id, customer_name, items):
    # Function implementation
    pass

process_order(500, 'akbar', ['milk'])


run_400(20)
run_500(20)
sum(1, 2, 3, 4)
multiply(2, 3, c=4)

# Processing order 500 for customer 'akbar' (execution time: 0.0000 secs)
# Finished main.run_500() (execution time: 0.0000 secs)
# Starting main.multiply() with args: a=2, b=3, c=4
# Finished main.multiply() with args: a=2, b=3, c=4 (execution time: 0.0000 secs)