import logging

from time_logger.profiling import profiling

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())


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


class NonStringConvertible:
    def __str__(self):
        raise ValueError("Cannot convert to string")
    
    def __repr__(self) -> str:
        return self.__str__()

@profiling(log_all_args=True)
def test_func(a, b):
    pass

test_func(NonStringConvertible(),2)