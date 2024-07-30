import inspect
import time
from contextlib import suppress
from functools import wraps
from inspect import iscoroutinefunction
from logging import Logger
from typing import Callable


def get_class(method):
    if inspect.ismethod(method):
        return method.__self__.__class__
    return None


class Profiler:
    def __init__(
        self,
        function: Callable,
        args,
        kwargs,
        logger: Logger,
        log_start: bool,
        log_args: bool,
        log_kwargs: str,
    ) -> None:
        self.main_function = function
        self.args = args
        self.kwargs = kwargs

        self.logger = logger
        self.log_start = log_start
        self.log_args = log_args
        self.log_kwargs = log_kwargs

    def log_arguments(self):
        print_args = ""
        print_kwargs = ""

        with suppress(Exception):
            if self.log_args:
                print_args = f"print_args={str(self.args)}"

            if self.log_kwargs == "all":
                print_kwargs = f"print_kwargs={str(self.kwargs)}"
            elif (
                self.log_kwargs
            ):  # Changed condition to check if log_kwargs is not None
                print_kwargs = f"print_kwargs={self.log_kwargs}:{self.kwargs.get(self.log_kwargs, None)}"

        return print_args, print_kwargs

    def start_log_logic(self):
        self.start_time = time.perf_counter()

        print_args, print_kwargs = self.log_arguments()
        if self.log_start and self.logger:
            cls = get_class(self.main_function)
            value_to_log = (
                f"Starting {cls.__name__}.{self.main_function.__name__}()"
                if cls
                else f"Started {self.main_function.__name__}()"
            )

            if print_args:
                value_to_log += f", {print_args}"

            if print_kwargs:
                value_to_log += f", {print_kwargs}"

            value_to_log += "\n"
            print(value_to_log)
            self.logger.info(value_to_log)

    def end_log_logic(
        self,
    ):
        end_time = time.perf_counter()
        run_time = end_time - self.start_time

        print_args, print_kwargs = self.log_arguments()
        if self.logger:
            cls = get_class(self.main_function)
            value_to_log = (
                f"Finished {cls.__name__}.{self.main_function.__name__}() in {run_time:.4f} secs"
                if cls
                else f"Finished {self.main_function.__name__}() in {run_time:.4f} secs"
            )

            if print_args:
                value_to_log += f", {print_args}"

            if print_kwargs:
                value_to_log += f", {print_kwargs}"

            value_to_log += "\n"
            print(value_to_log)
            self.logger.info(value_to_log)


def profiling(
    logger: Logger,
    log_start: bool = False,
    log_args: bool = False,
    log_kwargs: str = None,
):
    """
    We will write all the result into logger
    log_args can be true or false. If it is true, it will print all the args passed to the function in the log.
    log_kwargs can be None, "all" or argument_name to be logged.
    """

    def decorator(f):
        def create_profiler(*args, **kwargs):
            return Profiler(
                function=f,
                args=args,
                kwargs=kwargs,
                logger=logger,
                log_start=log_start,
                log_args=log_args,
                log_kwargs=log_kwargs,
            )
        @wraps(f)
        def wrapper(*args, **kwargs):
            profiler = create_profiler(*args, **kwargs)
            profiler.start_log_logic()
            output_value = f(*args, **kwargs)
            profiler.end_log_logic()
            return output_value

        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            profiler = create_profiler(*args, **kwargs)
            profiler.start_log_logic()
            output_value = await f(*args, **kwargs)
            profiler.end_log_logic()
            return output_value

        return async_wrapper if iscoroutinefunction(f) else wrapper

    return decorator
