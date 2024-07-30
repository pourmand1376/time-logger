import inspect
from logging import Logger

import time
from contextlib import suppress
from functools import wraps
from inspect import iscoroutinefunction

class LoggerProfile():
    def __init__(self, logger: Logger, log_start:bool,log_args:bool,log_kwargs:str) -> None:
        pass

    def get_class(self, method):
        if inspect.ismethod(method):
            return method.__self__.__class__
        return None

    def log_arguments(self, log_args,log_kwargs, *args, **kwargs):
        print_args = ""
        print_kwargs = ""

        with suppress(Exception):
            if log_args:
                print_args = f"print_args={str(args)}"

            if log_kwargs == "all":
                print_kwargs = f"print_kwargs={str(kwargs)}"
            elif log_kwargs:  # Changed condition to check if log_kwargs is not None
                print_kwargs = f"print_kwargs={log_kwargs}:{kwargs.get(log_kwargs, None)}"

        return print_args, print_kwargs

    def start_log_logic(self, func,logger, log_start,log_args,log_kwargs, *args, **kwargs):
        print_args, print_kwargs = self.log_arguments(log_args,log_kwargs,*args, **kwargs)
        if log_start and logger:
            cls = get_class(func)
            value_to_log = (
                f"Starting {cls.__name__}.{func.__name__}()"
                if cls
                else f"Started {func.__name__}()"
            )

            if print_args:
                value_to_log += f", {print_args}"

            if print_kwargs:
                value_to_log += f", {print_kwargs}"

            value_to_log += "\n"
            print(value_to_log)
            logger.info(value_to_log)

    def end_log_logic(self, func,logger, log_start,log_args,log_kwargs, start_time, *args, **kwargs):
        end_time = time.perf_counter()
        run_time = end_time - start_time

        print_args, print_kwargs = self.log_arguments(log_args,log_kwargs, *args, **kwargs)
        if logger:
            cls = self.get_class(func)
            value_to_log = (
                f"Finished {cls.__name__}.{func.__name__}() in {run_time:.4f} secs"
                if cls
                else f"Finished {func.__name__}() in {run_time:.4f} secs"
            )

            if print_args:
                value_to_log += f", {print_args}"

            if print_kwargs:
                value_to_log += f", {print_kwargs}"

            value_to_log += "\n"
            print(value_to_log)
            logger.info(value_to_log)


def profiling(logger: Logger,
              log_start: bool=False,
               log_args: bool = False,
                log_kwargs: str = None,
                ):
    """
    We will write all the result into logger
    log_args can be true or false. If it is true, it will print all the args passed to the function in the log.
    log_kwargs can be None, "all" or argument_name to be logged.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_log_logic(f,  *args, **kwargs)
            start_time = time.perf_counter()
            output_value = f(*args, **kwargs)
            end_log_logic(f, logger, log_start, log_args, log_kwargs, start_time, *args, **kwargs)
            return output_value

        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            start_log_logic(f, logger, log_start,log_args,log_kwargs, *args, **kwargs)
            start_time = time.perf_counter()
            output_value = await f(*args, **kwargs)
            end_log_logic(f, logger, log_start, log_args, log_kwargs, start_time, *args, **kwargs)
            return output_value

        return async_wrapper if iscoroutinefunction(f) else wrapper
    return decorator