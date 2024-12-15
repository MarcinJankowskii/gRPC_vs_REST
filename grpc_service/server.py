from concurrent import futures
import grpc
import service_pb2
import service_pb2_grpc

class ProcessService(service_pb2_grpc.ProcessServiceServicer):
    def Process(self, request, context):
        result = sum(request.numbers)
        return service_pb2.ProcessResponse(result=result)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
    ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
    ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MB
])
    service_pb2_grpc.add_ProcessServiceServicer_to_server(ProcessService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
