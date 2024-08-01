import logging

from profiling import profiling

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

@profiling(log_start=True)
def run_400(time=200):
    for i in range(time):
        i *= i


@profiling(logger=None, log_start=False)
def run_500(time=200):
    for i in range(time):
        i *= i


@profiling(logger=logger, log_args=True, log_start=True)
def sum(*args):
    sum = 0
    for i in args:
        sum += i
    return sum


run_400(20)
run_500(20)
sum(1, 2, 3, 4)
