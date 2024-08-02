import time
from functools import wraps
from inspect import iscoroutinefunction, signature
from logging import Logger
from typing import Callable, Optional, List, Dict
import re
import traceback

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
        custom_message: Optional[str] = None,
    ) -> None:
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.logger = logger
        self.log_start = log_start
        self.log_all_args = log_all_args
        self.custom_message = custom_message
        self.log_variables = log_variables if log_variables is not None else self._extract_variables_from_custom_message()
        self.start_time = 0.0
        self.module_name = self._get_module_name()

    def _extract_variables_from_custom_message(self) -> List[str]:
        if not self.custom_message:
            return []
        return re.findall(r'\{(\w+)\}', self.custom_message)

    def _format_variables(self) -> Dict[str, str]:
        func_signature = signature(self.function)
        bound_args = func_signature.bind(*self.args, **self.kwargs)
        bound_args.apply_defaults()

        if self.log_all_args:
            return {k: repr(v) for k, v in bound_args.arguments.items()}

        return {
            var_name: repr(bound_args.arguments[var_name])
            for var_name in self.log_variables
            if var_name in bound_args.arguments
        }

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

    def _log_error(self, error:Exception) -> None:
        if self.logger:
            self.logger.exception(repr(error), exc_info=True)
        else:
            print(f"{type(error).__name__} at line {error.__traceback__.tb_lineno} of {__file__}: {error}")

        traceback.print_exc()


    def _log_message(
        self, action: str, run_time: Optional[float] = None
    ) -> None:
        formatted_vars = self._format_variables()

        if self.custom_message:
            try:
                message = self.custom_message.format(**formatted_vars)
            except KeyError as e:
                message = f"Error in custom message: {str(e)}. Using default format."
                self.custom_message = None  # Fall back to default format

        if not self.custom_message:
            func_name = self._get_full_function_name()
            variables = ", ".join(f"{k}={v}" for k, v in formatted_vars.items())

            message = f"{action} {func_name}()"
            if variables:
                message += f" with args: {variables}"

        if run_time is not None:
            message += f" (execution time: {run_time:.4f} secs)"

        self._log(message)

    def start(self) -> None:
        try:
            self.start_time = time.perf_counter()
            if self.log_start:
                self._log_message("Starting")
        except Exception as error:
            self._log_error(error)

    def end(self) -> None:
        try:
            run_time = time.perf_counter() - self.start_time
            self._log_message("Finished", run_time)
        except Exception as error:
            self._log_error(error)




def profiling(
    logger: Optional[Logger] = None,
    log_start: bool = False,
    log_variables: Optional[List[str]] = None,
    log_all_args: bool = False,
    custom_message: Optional[str] = None,
):
    """
    We will write all the result into logger if provided, otherwise use print
    log_start: If True, log when the function starts.
    log_variables: A list of variable names to log when using the default message format.
                   If custom_message is provided, this parameter is ignored and variables
                   are extracted from the custom_message.
    log_all_args: If True, log all arguments passed to the function.
    custom_message: If provided, this message will be used instead of the default logging format.
                    Variables can be included using curly braces, e.g., {variable_name}.
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
                custom_message=custom_message,
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