import time
from functools import wraps
from inspect import iscoroutinefunction
from logging import Logger
from typing import Callable, Optional, Union


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
        self.module_name = self._get_module_name()

    def _format_arguments(self) -> tuple[str, str]:
        print_args = f"args={str(self.args)}" if self.log_args else ""
        print_kwargs = ""

        if self.log_kwargs == "all":
            print_kwargs = f"kwargs={str(self.kwargs)}"
        elif self.log_kwargs:
            print_kwargs = (
                f"{self.log_kwargs}={self.kwargs.get(self.log_kwargs)}"
            )

        return print_args, print_kwargs

    def _get_module_name(self) -> str:
        module = self.function.__module__
        if module is None or module == str.__class__.__module__:
            return ""
        if module == "__main__":
            return "main"
        return module

    def _get_function_name(self) -> str:
        cls = (
            self.function.__self__.__class__
            if hasattr(self.function, "__self__")
            else None
        )
        return (
            f"{cls.__name__}.{self.function.__name__}"
            if cls
            else self.function.__name__
        )

    def _get_full_function_name(self) -> str:
        func_name = self._get_function_name()
        if self.module_name:
            return f"{self.module_name}.{func_name}"
        return func_name

    def _log(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def _log_message(
        self, action: str, run_time: Optional[float] = None
    ) -> None:
        func_name = self._get_full_function_name()
        args, kwargs = self._format_arguments()

        message = f"{action} {func_name}()"
        if run_time is not None:
            message += f" in {run_time:.4f} secs"
        if args:
            message += f", {args}"
        if kwargs:
            message += f", {kwargs}"

        self._log(message)

    def start(self) -> None:
        self.start_time = time.perf_counter()
        if self.log_start:
            self._log_message("Starting")

    def end(self) -> None:
        run_time = time.perf_counter() - self.start_time
        self._log_message("Finished", run_time)


def profiling(
    logger: Optional[Logger] = None,
    log_start: bool = False,
    log_args: bool = False,
    log_kwargs: Optional[str] = None,
):
    """
    We will write all the result into logger if provided, otherwise use print
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