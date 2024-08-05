import pytest
import logging
from io import StringIO
from unittest.mock import patch, MagicMock
from src.time_logger.profiling import Profiler

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
    assert profiler._get_module_name() == "tests.test_profiler"

def test_get_function_name():
    def test_func():
        pass
    
    profiler = Profiler(test_func, (), {})
    assert profiler._get_function_name() == "test_func"

def test_get_full_function_name():
    def test_func():
        pass
    
    profiler = Profiler(test_func, (), {})
    assert profiler._get_full_function_name() == "tests.test_profiler.test_func"

def test_log_message(logger):
    logger, log_capture = logger
    def test_func(a, b):
        pass
    
    profiler = Profiler(test_func, (1, 2), {}, logger, log_variables=['a', 'b'])
    profiler._log_message("Starting")
    
    log_output = log_capture.getvalue()
    assert "Starting tests.test_profiler.test_func() with args: a=1, b=2" in log_output

def test_log_message_custom(logger):
    logger, log_capture = logger
    def test_func(a, b):
        pass
    
    profiler = Profiler(test_func, (1, 2), {}, logger, custom_message="Custom {a} and {b}")
    profiler._log_message("Starting")
    
    log_output = log_capture.getvalue()
    assert "Custom 1 and 2" in log_output

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
    assert "Starting tests.test_profiler.test_func() with args: a=1, b=2" in log_output
    assert "Finished tests.test_profiler.test_func() with args: a=1, b=2 (execution time: 1.0000 secs)" in log_output

def test_log_message_error_handling(logger):
    logger, log_capture = logger
    
    def test_func(a, b):
        pass
    
    # Provide both 'a' and 'b' arguments
    profiler = Profiler(test_func, (1,), {'b': 2}, logger, custom_message="Custom {a} and {b}")
    profiler._log_message("Starting")
    
    log_output = log_capture.getvalue()
    assert "Custom 1 and 2" in log_output
    assert "Error in custom message" not in log_output
    assert "Using default format" not in log_output

def test_profiler_no_logger():
    def test_func():
        pass
    
    profiler = Profiler(test_func, (), {})
    with patch('builtins.print') as mock_print:
        profiler._log_message("Test")
        mock_print.assert_called_once()

def test_profiler_with_method():
    class TestClass:
        def test_method(self):
            pass
    
    obj = TestClass()
    profiler = Profiler(obj.test_method, (), {})
    assert profiler._get_function_name() == "TestClass.test_method"

def test_profiler_with_lambda():
    lambda_func = lambda x: x * 2
    profiler = Profiler(lambda_func, (2,), {})
    assert profiler._get_function_name() == "<lambda>"

def test_profiler_with_invalid_argument(logger):
    logger, log_capture = logger
    
    def test_func(a, b):
        pass
    
    # Pass an invalid argument 'c' which is not a parameter of test_func
    profiler = Profiler(test_func, (1, 2), {}, logger, log_variables=['a', 'b', 'c'])
    
    # This should not raise an error
    profiler._log_message("Starting")
    
    log_output = log_capture.getvalue()
    
    # Check that the valid arguments are logged
    assert "Starting tests.test_profiler.test_func() with args: a=1, b=2" in log_output
    
    # The invalid argument 'c' should not appear in the log
    assert "c=" not in log_output
    
    # Ensure no error message is logged
    assert "Error in custom message" not in log_output
    assert "Using default format" not in log_output
