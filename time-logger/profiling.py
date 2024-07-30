import inspect
import time
from contextlib import suppress
from functools import wraps
from inspect import iscoroutinefunction
from logging import Logger
from typing import Callable, Optional


def get_class(method):
    if inspect.ismethod(method):
        return method.__self__.__class__
    return None


class Profiler:
    def __init__(
        self,
        function: Callable,
        args: tuple,
        kwargs: dict,
        logger: Optional[Logger] = None,
        log_start: bool = True,
        log_args: bool = False,
        log_kwargs: Optional[str] = None,
    ) -> None:
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.logger = logger
        self.log_start = log_start
        self.log_args = log_args
        self.log_kwargs = log_kwargs
        self.start_time = 0.0

    def _format_arguments(self) -> tuple[str, str]:
        print_args = f"args={str(self.args)}" if self.log_args else ""
        print_kwargs = ""
        
        if self.log_kwargs == "all":
            print_kwargs = f"kwargs={str(self.kwargs)}"
        elif self.log_kwargs:
            print_kwargs = f"{self.log_kwargs}={self.kwargs.get(self.log_kwargs)}"
        
        return print_args, print_kwargs

    def _get_function_name(self) -> str:
        cls = self.function.__self__.__class__ if hasattr(self.function, '__self__') else None
        return f"{cls.__name__}.{self.function.__name__}" if cls else self.function.__name__

    def _log_message(self, action: str, run_time: Optional[float] = None) -> None:
        if not self.logger:
            return

        func_name = self._get_function_name()
        args, kwargs = self._format_arguments()
        
        message = f"{action} {func_name}()"
        if run_time is not None:
            message += f" in {run_time:.4f} secs"
        if args:
            message += f", {args}"
        if kwargs:
            message += f", {kwargs}"

        print(message)
        self.logger.info(message)

    def start(self) -> None:
        self.start_time = time.perf_counter()
        if self.log_start:
            self._log_message("Starting")

    def end(self) -> None:
        run_time = time.perf_counter() - self.start_time
        self._log_message("Finished", run_time)



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
            profiler.start()
            output_value = f(*args, **kwargs)
            profiler.end()
            return output_value

        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            profiler = create_profiler(*args, **kwargs)
            profiler.start()
            output_value = await f(*args, **kwargs)
            profiler.end()
            return output_value

        return async_wrapper if iscoroutinefunction(f) else wrapper

    return decorator
