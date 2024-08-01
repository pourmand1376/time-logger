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


run_400(20)
run_500(20)
sum(1, 2, 3, 4)
multiply(2, 3, c=4)
