import asyncio
import logging
from io import StringIO
from unittest.mock import patch

import pytest

# Import the module containing the Profiler and profiling decorator
from src.time_logger.profiling import Profiler, profiling


@pytest.fixture
def logger():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)
    return logger, log_capture

def test_profiler_init(logger):
    logger, _ = logger
    def test_func(a, b):
        pass

    profiler = Profiler(test_func, (1, 2), {}, logger, True, ['a'], False, None)
    assert profiler.function == test_func
    assert profiler.args == (1, 2)
    assert profiler.kwargs == {}
    assert profiler.logger == logger
    assert profiler.log_start == True
    assert profiler.log_variables == ['a']
    assert profiler.log_all_args == False
    assert profiler.custom_message == None

def test_extract_variables_from_custom_message():
    def test_func():
        pass

    profiler = Profiler(test_func, (), {}, custom_message="Test {var1} and {var2}")
    assert profiler.log_variables == ['var1', 'var2']

def test_format_variables():
    def test_func(a, b, c=3):
        pass

    profiler = Profiler(test_func, (1, 2), {'c': 4}, log_variables=['a', 'c'])
    formatted_vars = profiler._format_variables()
    assert formatted_vars == {'a': '1', 'c': '4'}

def test_format_variables_log_all_args():
    def test_func(a, b, c=3):
        pass

    profiler = Profiler(test_func, (1, 2), {'c': 4}, log_all_args=True)
    formatted_vars = profiler._format_variables()
    assert formatted_vars == {'a': '1', 'b': '2', 'c': '4'}

def test_get_module_name():
    def test_func():
        pass

    profiler = Profiler(test_func, (), {})
    assert profiler._get_module_name() == "tests.test_general"

def test_get_function_name():
    def test_func():
        pass

    profiler = Profiler(test_func, (), {})
    assert profiler._get_function_name() == "test_func"

def test_get_full_function_name():
    def test_func():
        pass

    profiler = Profiler(test_func, (), {})
    assert profiler._get_full_function_name() == "tests.test_general.test_func"

@patch('time.perf_counter')
def test_start_and_end(mock_perf_counter, logger):
    logger, log_capture = logger
    mock_perf_counter.side_effect = [0, 1]  # Start time and end time

    def test_func(a, b):
        pass

    profiler = Profiler(test_func, (1, 2), {}, logger, True, ['a', 'b'])
    profiler.start()
    profiler.end()

    log_output = log_capture.getvalue()
    assert "Starting tests.test_general.test_func() with args: a=1, b=2" in log_output
    assert "Finished tests.test_general.test_func() with args: a=1, b=2 (execution time: 1.0000 secs)" in log_output

def test_custom_message(logger):
    logger, log_capture = logger
    def test_func(a, b):
        pass

    profiler = Profiler(test_func, (1, 2), {}, logger, True, custom_message="Custom {a} and {b}")
    profiler.start()

    log_output = log_capture.getvalue()
    assert "Custom 1 and 2" in log_output

@patch('time.perf_counter')
def test_profiling_decorator(mock_perf_counter, logger):
    logger, log_capture = logger
    mock_perf_counter.side_effect = [0, 1]  # Start time and end time

    @profiling(logger, log_start=True, log_variables=['a'])
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)

    assert result == 3
    log_output = log_capture.getvalue()
    assert "Starting tests.test_general.test_func() with args: a=1" in log_output
    assert "Finished tests.test_general.test_func() with args: a=1 (execution time: 1.0000 secs)" in log_output

@pytest.mark.asyncio
@patch('time.perf_counter')
async def test_profiling_decorator_async(mock_perf_counter, logger):
    logger, log_capture = logger
    mock_perf_counter.side_effect = [0, 1]  # Start time and end time

    @profiling(logger, log_start=True, log_variables=['a'])
    async def test_func(a, b):
        await asyncio.sleep(0)
        return a + b

    result = await test_func(1, 2)
    assert result == 3
    log_output = log_capture.getvalue()
    assert "Starting tests.test_general.test_func() with args: a=1" in log_output
    assert "Finished tests.test_general.test_func() with args: a=1 (execution time: 1.0000 secs)" in log_output

def test_profiling_decorator_log_all_args(logger):
    logger, log_capture = logger

    @profiling(logger, log_all_args=True)
    def test_func(a, b, c=3):
        return a + b + c

    result = test_func(1, 2, c=4)

    assert result == 7
    log_output = log_capture.getvalue()
    assert "Finished tests.test_general.test_func() with args: a=1, b=2, c=4" in log_output

def test_profiling_decorator_custom_message(logger):
    logger, log_capture = logger

    @profiling(logger, custom_message="Custom {a} and {b}")
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)

    assert result == 3
    log_output = log_capture.getvalue()
    assert "Custom 1 and 2" in log_output