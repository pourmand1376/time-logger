import pytest
import asyncio
import logging
from io import StringIO
from unittest.mock import patch
from src.time_logger.profiling import profiling

@pytest.fixture
def logger():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)
    return logger, log_capture

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
    assert "Starting tests.test_profiling_decorator.test_func() with args: a=1" in log_output
    assert "Finished tests.test_profiling_decorator.test_func() with args: a=1 (execution time: 1.0000 secs)" in log_output

def test_profiling_decorator_log_all_args(logger):
    logger, log_capture = logger

    @profiling(logger, log_all_args=True)
    def test_func(a, b, c=3):
        return a + b + c

    result = test_func(1, 2, c=4)

    assert result == 7
    log_output = log_capture.getvalue()
    assert "Finished tests.test_profiling_decorator.test_func() with args: a=1, b=2, c=4" in log_output

def test_profiling_decorator_custom_message(logger):
    logger, log_capture = logger

    @profiling(logger, custom_message="Custom {a} and {b}")
    def test_func(a, b):
        return a + b

    result = test_func(1, 2)

    assert result == 3
    log_output = log_capture.getvalue()
    assert "Custom 1 and 2" in log_output

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
    assert "Starting tests.test_profiling_decorator.test_func() with args: a=1" in log_output
    assert "Finished tests.test_profiling_decorator.test_func() with args: a=1 (execution time: 1.0000 secs)" in log_output

def test_profiling_decorator_no_logger():
    @profiling()
    def test_func():
        return "test"

    with patch('builtins.print') as mock_print:
        result = test_func()
        assert result == "test"
        mock_print.assert_called()


@pytest.mark.parametrize("log_start,expected", [
    (True, 2),  # Both start and end logs
    (False, 1),  # Only end log
])
def test_profiling_decorator_log_start(logger, log_start, expected):
    logger, log_capture = logger

    @profiling(logger, log_start=log_start)
    def test_func():
        pass

    test_func()
    log_output = log_capture.getvalue()
    assert log_output.count("tests.test_profiling_decorator.test_func()") == expected

def test_profiling_decorator_nested(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['a'],log_start=True)
    def outer(a):
        @profiling(logger, log_variables=['b'])
        def inner(b):
            return b * 2
        return inner(a + 1)

    result = outer(2)
    assert result == 6

    log_output = log_capture.getvalue()
    assert "Starting tests.test_profiling_decorator.outer() with args: a=2" in log_output
    assert "Finished tests.test_profiling_decorator.inner() with args: b=3" in log_output
    assert "Finished tests.test_profiling_decorator.outer() with args: a=2" in log_output