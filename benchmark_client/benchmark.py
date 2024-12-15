import time
import sys
sys.path.append('../grpc_service')
import requests
import grpc
import service_pb2
import service_pb2_grpc
import concurrent.futures
import psutil

def benchmark_rest():
    url = "http://localhost:5000/process"
    payload = {"numbers": list(range(100))}
    start = time.time()
    requests.post(url, json=payload, timeout=5)
    elapsed = time.time() - start
    return elapsed

def benchmark_grpc():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.ProcessServiceStub(channel)
        start = time.time()
        stub.Process(service_pb2.ProcessRequest(numbers=list(range(100))))
        elapsed = time.time() - start
    return elapsed

def benchmark_multiple_requests(service_type, num_requests):
    elapsed = 0
    if service_type == 'rest':
        url = "http://localhost:5000/process"
        payload = {"numbers": list(range(100))}
        start = time.time()
        for _ in range(num_requests):
            requests.post(url, json=payload)
        elapsed = time.time() - start
    elif service_type == 'grpc':
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = service_pb2_grpc.ProcessServiceStub(channel)
            start = time.time()
            for _ in range(num_requests):
                stub.Process(service_pb2.ProcessRequest(numbers=list(range(100))))
            elapsed = time.time() - start
    return elapsed

def send_request(service_type):
    if service_type == 'rest':
        url = "http://localhost:5000/process"
        payload = {"numbers": list(range(100))}
        requests.post(url, json=payload)
    elif service_type == 'grpc':
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = service_pb2_grpc.ProcessServiceStub(channel)
            stub.Process(service_pb2.ProcessRequest(numbers=list(range(100))))

def benchmark_concurrent_requests(service_type, num_threads):
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(send_request, service_type) for _ in range(num_threads)]
        concurrent.futures.wait(futures)
    elapsed = time.time() - start
    return elapsed

def benchmark_data_size_chunked(service_type, data_size, chunk_size=10000):
    data = list(range(data_size))
    elapsed = 0
    if service_type == 'rest':
        url = "http://localhost:5000/process"
        for chunk_start in range(0, data_size, chunk_size):
            payload = {"numbers": data[chunk_start:chunk_start + chunk_size]}
            start = time.time()
            requests.post(url, json=payload)
            elapsed += time.time() - start
    elif service_type == 'grpc':
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = service_pb2_grpc.ProcessServiceStub(channel)
            for chunk_start in range(0, data_size, chunk_size):
                chunk = data[chunk_start:chunk_start + chunk_size]
                start = time.time()
                stub.Process(service_pb2.ProcessRequest(numbers=chunk))
                elapsed += time.time() - start
    return elapsed

def benchmark_requests(service_type, num_requests):
    elapsed = 0
    if service_type == 'rest':
        url = "http://localhost:5000/process"
        payload = {"numbers": list(range(100))}
        start = time.time()
        for _ in range(num_requests):
            requests.post(url, json=payload)
        elapsed = time.time() - start
    elif service_type == 'grpc':
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = service_pb2_grpc.ProcessServiceStub(channel)
            start = time.time()
            for _ in range(num_requests):
                stub.Process(service_pb2.ProcessRequest(numbers=list(range(100))))
            elapsed = time.time() - start
    return elapsed

def measure_resource_usage(service_type, num_requests):
    process = psutil.Process()
    start_cpu = process.cpu_percent(interval=None)
    start_mem = process.memory_info().rss

    elapsed = benchmark_requests(service_type, num_requests)

    end_cpu = process.cpu_percent(interval=None)
    end_mem = process.memory_info().rss

    cpu_usage = end_cpu - start_cpu
    mem_usage = (end_mem - start_mem) / 1024 / 1024  # Convert to MB

    return elapsed, cpu_usage, mem_usage

if __name__ == "__main__":
    # Run benchmark for single request
    rest_time = benchmark_rest()
    grpc_time = benchmark_grpc()
    print(f"REST time: {rest_time:.4f}s")
    print(f"gRPC time: {grpc_time:.4f}s")

    # Run benchmark for multiple requests
    for n in [1, 10, 100, 1000, 10000]:
        rest_time = benchmark_multiple_requests('rest', n)
        grpc_time = benchmark_multiple_requests('grpc', n)
        print(f"Requests: {n}, REST time: {rest_time:.4f}s, gRPC time: {grpc_time:.4f}s")

    # Run benchmark for concurrent requests
    for threads in [1, 10, 100, 1000, 10000]:
        rest_time = benchmark_concurrent_requests('rest', threads)
        grpc_time = benchmark_concurrent_requests('grpc', threads)
        print(f"Threads: {threads}, REST time: {rest_time:.4f}s, gRPC time: {grpc_time:.4f}s")

    # Run benchmark for data size chunking
    for size in [10, 100, 1000, 10000, 100000]:
        rest_time = benchmark_data_size_chunked('rest', size)
        grpc_time = benchmark_data_size_chunked('grpc', size)
        print(f"Data size: {size}, REST time: {rest_time:.4f}s, gRPC time: {grpc_time:.4f}s")

    # Run benchmark for resource usage
    for n in [100, 1000, 10000]:
        rest_time, rest_cpu, rest_mem = measure_resource_usage('rest', n)
        grpc_time, grpc_cpu, grpc_mem = measure_resource_usage('grpc', n)
        print(f"Requests: {n}, REST: {rest_time:.4f}s, CPU: {rest_cpu:.2f}%, MEM: {rest_mem:.2f}MB")
        print(f"Requests: {n}, gRPC: {grpc_time:.4f}s, CPU: {grpc_cpu:.2f}%, MEM: {grpc_mem:.2f}MB")