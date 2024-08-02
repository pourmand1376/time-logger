import pytest
import asyncio
import logging
from io import StringIO
from unittest.mock import patch
from time_logger.profiling import profiling, Profiler

@pytest.fixture
def logger():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)
    return logger, log_capture

def test_profiler_with_decorator(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['x'])
    def test_func(x, y):
        profiler = Profiler(sum, (x, y), {}, logger, log_variables=['0', '1'])
        profiler.start()
        result = sum((x, y))
        profiler.end()
        return result

    result = test_func(3, 4)
    assert result == 7

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_integration.test_func() with args: x=3" in log_output
    assert "Starting builtins.sum() with args: 0=3, 1=4" in log_output
    assert "Finished builtins.sum() with args: 0=3, 1=4" in log_output
    assert "Finished test_profiling_integration.test_func() with args: x=3" in log_output

def test_nested_profiling(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['a'])
    def outer(a, b):
        @profiling(logger, log_variables=['x'])
        def inner(x, y):
            return x * y
        return inner(a, b)

    result = outer(2, 3)
    assert result == 6

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_integration.outer() with args: a=2" in log_output
    assert "Starting test_profiling_integration.inner() with args: x=2" in log_output
    assert "Finished test_profiling_integration.inner() with args: x=2" in log_output
    assert "Finished test_profiling_integration.outer() with args: a=2" in log_output

def test_profiling_with_different_logger_levels(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['x'])
    def test_func(x):
        return x * 2

    logger.setLevel(logging.DEBUG)
    test_func(5)
    debug_output = log_capture.getvalue()

    log_capture.truncate(0)
    log_capture.seek(0)

    logger.setLevel(logging.WARNING)
    test_func(5)
    warning_output = log_capture.getvalue()

    assert len(debug_output) > len(warning_output)

@pytest.mark.asyncio
async def test_profiling_in_async_context(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['x'])
    async def async_func1(x):
        await asyncio.sleep(0.1)
        return x * 2

    @profiling(logger, log_variables=['y'])
    async def async_func2(y):
        await asyncio.sleep(0.1)
        return y + 3

    results = await asyncio.gather(async_func1(2), async_func2(3))
    assert results == [4, 6]

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_integration.async_func1() with args: x=2" in log_output
    assert "Starting test_profiling_integration.async_func2() with args: y=3" in log_output
    assert "Finished test_profiling_integration.async_func1() with args: x=2" in log_output
    assert "Finished test_profiling_integration.async_func2() with args: y=3" in log_output

@patch('time.perf_counter')
def test_profiling_accuracy(mock_perf_counter, logger):
    logger, log_capture = logger
    mock_perf_counter.side_effect = [0, 0.5, 1, 1.5]  # Start and end times for two functions

    @profiling(logger)
    def func1():
        pass

    @profiling(logger)
    def func2():
        pass

    func1()
    func2()

    log_output = log_capture.getvalue()
    assert "execution time: 0.5000 secs" in log_output
    assert "execution time: 0.5000 secs" in log_output

def test_profiling_with_generator(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['n'])
    def generate_numbers(n):
        for i in range(n):
            yield i

    list(generate_numbers(3))

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_integration.generate_numbers() with args: n=3" in log_output
    assert "Finished test_profiling_integration.generate_numbers() with args: n=3" in log_output

def test_profiling_with_recursion(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['n'])
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    result = factorial(5)
    assert result == 120

    log_output = log_capture.getvalue()
    assert log_output.count("Starting test_profiling_integration.factorial()") == 5
    assert log_output.count("Finished test_profiling_integration.factorial()") == 5

def test_profiling_with_exception(logger):
    logger, log_capture = logger

    @profiling(logger)
    def error_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        error_function()

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_integration.error_function()" in log_output
    assert "Finished test_profiling_integration.error_function()" in log_output
    assert "execution time:" in log_output

@pytest.mark.parametrize("input_value,expected_output", [
    (2, 4),
    (0, 0),
    (-3, -6)
])
def test_profiling_with_different_inputs(logger, input_value, expected_output):
    logger, log_capture = logger

    @profiling(logger, log_variables=['x'])
    def double(x):
        return x * 2

    result = double(input_value)
    assert result == expected_output

    log_output = log_capture.getvalue()
    assert f"with args: x={input_value}" in log_output