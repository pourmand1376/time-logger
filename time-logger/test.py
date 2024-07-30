from profiling import profiling
import logging
import sys

logger=logging.getLogger()
logger.addHandler(logging.StreamHandler())

@profiling(logger=logger, log_start=True)
def run_400(time= 200):
    for i in range(time):
        i *= i

@profiling(logger=logger, log_start=False)
def run_500(time= 200):
    for i in range(time):
        i *= i

run_400(20)
run_500(20)