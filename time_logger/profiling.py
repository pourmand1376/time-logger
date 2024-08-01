import time
from functools import wraps
from inspect import iscoroutinefunction, signature
from logging import Logger
from typing import Callable, Optional, Union, List


class Profiler:
    def __init__(
        self,
        function: Callable,
        args: tuple,
        kwargs: dict,
        logger: Optional[Logger] = None,
        log_start: bool = True,
        log_variables: Optional[List[str]] = None,
        log_all_args: bool = False,
    ) -> None:
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.logger = logger
        self.log_start = log_start
        self.log_variables = log_variables or []
        self.log_all_args = log_all_args
        self.start_time = 0.0
        self.module_name = self._get_module_name()

    def _format_variables(self) -> str:
        func_signature = signature(self.function)
        bound_args = func_signature.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        if self.log_all_args:
            return ", ".join(f"{k}={repr(v)}" for k, v in bound_args.arguments.items())

        logged_vars = []
        for var_name in self.log_variables:
            if var_name in bound_args.arguments:
                value = bound_args.arguments[var_name]
                logged_vars.append(f"{var_name}={repr(value)}")

        return ", ".join(logged_vars)

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
        variables = self._format_variables()

        message = f"{action} {func_name}()"
        if run_time is not None:
            message += f" in {run_time:.4f} secs"
        if variables:
            message += f" with args: {variables}"

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
    log_variables: Optional[List[str]] = None,
    log_all_args: bool = False,
):
    """
    We will write all the result into logger if provided, otherwise use print
    log_start: If True, log when the function starts.
    log_variables: A list of variable names to log. These can be positional or keyword arguments of the decorated function.
    log_all_args: If True, log all arguments passed to the function, regardless of log_variables.
    """

    def decorator(f):
        def create_profiler(*args, **kwargs):
            return Profiler(
                function=f,
                args=args,
                kwargs=kwargs,
                logger=logger,
                log_start=log_start,
                log_variables=log_variables,
                log_all_args=log_all_args,
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