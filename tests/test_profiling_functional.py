import pytest
import time
import asyncio
import logging
from io import StringIO
from concurrent.futures import ThreadPoolExecutor
from time_logger.profiling import profiling

@pytest.fixture
def logger():
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)
    return logger, log_capture

def test_profiling_real_world_function(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['n'])
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    result = fibonacci(10)
    assert result == 55

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_functional.fibonacci() with args: n=10" in log_output
    assert "Finished test_profiling_functional.fibonacci() with args: n=10" in log_output
    assert "execution time:" in log_output

def test_profiling_with_external_dependencies(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['url'])
    def fetch_url_content(url):
        import requests
        response = requests.get(url)
        return response.text[:100]  # Return first 100 characters

    content = fetch_url_content('https://www.example.com')
    assert len(content) == 100

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_functional.fetch_url_content() with args: url=https://www.example.com" in log_output
    assert "Finished test_profiling_functional.fetch_url_content() with args: url=https://www.example.com" in log_output
    assert "execution time:" in log_output

def test_profiling_performance_impact():
    def heavy_computation(n):
        return sum(i * i for i in range(n))

    @profiling()
    def profiled_heavy_computation(n):
        return sum(i * i for i in range(n))

    n = 1000000
    
    start = time.perf_counter()
    result1 = heavy_computation(n)
    end = time.perf_counter()
    normal_time = end - start

    start = time.perf_counter()
    result2 = profiled_heavy_computation(n)
    end = time.perf_counter()
    profiled_time = end - start

    assert result1 == result2
    assert profiled_time < normal_time * 1.1  # Allowing 10% overhead

def test_profiling_in_multithreaded_environment(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['i'])
    def worker(i):
        time.sleep(0.1)
        return i * i

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(worker, range(10)))

    assert results == [i*i for i in range(10)]

    log_output = log_capture.getvalue()
    for i in range(10):
        assert f"Starting test_profiling_functional.worker() with args: i={i}" in log_output
        assert f"Finished test_profiling_functional.worker() with args: i={i}" in log_output

@pytest.mark.asyncio
async def test_profiling_in_async_web_application(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['user_id'])
    async def fetch_user_data(user_id):
        await asyncio.sleep(0.1)  # Simulating database query
        return {'id': user_id, 'name': f'User {user_id}'}

    @profiling(logger, log_variables=['user_id'])
    async def fetch_user_posts(user_id):
        await asyncio.sleep(0.1)  # Simulating database query
        return [f'Post {i} by User {user_id}' for i in range(3)]

    @profiling(logger, log_variables=['user_id'])
    async def get_user_info(user_id):
        user_data, user_posts = await asyncio.gather(
            fetch_user_data(user_id),
            fetch_user_posts(user_id)
        )
        return {**user_data, 'posts': user_posts}

    user_info = await get_user_info(42)
    assert user_info['id'] == 42
    assert user_info['name'] == 'User 42'
    assert len(user_info['posts']) == 3

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_functional.get_user_info() with args: user_id=42" in log_output
    assert "Starting test_profiling_functional.fetch_user_data() with args: user_id=42" in log_output
    assert "Starting test_profiling_functional.fetch_user_posts() with args: user_id=42" in log_output
    assert "Finished test_profiling_functional.fetch_user_data() with args: user_id=42" in log_output
    assert "Finished test_profiling_functional.fetch_user_posts() with args: user_id=42" in log_output
    assert "Finished test_profiling_functional.get_user_info() with args: user_id=42" in log_output

def test_profiling_with_large_input(logger):
    logger, log_capture = logger

    @profiling(logger, log_variables=['size'])
    def process_large_data(size):
        data = [i for i in range(size)]
        return sum(data)

    result = process_large_data(1000000)
    assert result == 499999500000

    log_output = log_capture.getvalue()
    assert "Starting test_profiling_functional.process_large_data() with args: size=1000000" in log_output
    assert "Finished test_profiling_functional.process_large_data() with args: size=1000000" in log_output
    assert "execution time:" in log_output

def test_profiling_with_different_log_levels(logger):
    logger, _ = logger

    @profiling(logger, log_variables=['x'])
    def sample_function(x):
        return x * 2

    logger.setLevel(logging.DEBUG)
    sample_function(5)

    logger.setLevel(logging.INFO)
    sample_function(10)

    logger.setLevel(logging.WARNING)
    sample_function(15)

    # Check log records
    debug_records = [record for record in logger.handlers[0].records if record.levelno == logging.DEBUG]
    info_records = [record for record in logger.handlers[0].records if record.levelno == logging.INFO]
    warning_records = [record for record in logger.handlers[0].records if record.levelno == logging.WARNING]

    assert len(debug_records) > 0
    assert len(info_records) > 0
    assert len(warning_records) == 0