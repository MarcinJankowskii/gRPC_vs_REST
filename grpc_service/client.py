import grpc
import service_pb2
import service_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051', options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
        ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
    ]) as channel:
        stub = service_pb2_grpc.ProcessServiceStub(channel)
        response = stub.Process(service_pb2.ProcessRequest(numbers=[1, 2, 3]))
        print(f"Result: {response.result}")

if __name__ == "__main__":
    run()
