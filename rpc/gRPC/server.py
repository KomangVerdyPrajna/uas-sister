import grpc
from concurrent import futures
import processor_pb2
import processor_pb2_grpc

class VisualProcessor(processor_pb2_grpc.DataProcessorServicer):
    def TransformText(self, request, context):
        # The actual function logic
        raw = request.input_text
        processed = raw.upper()
        count = len(raw)
        
        print(f"[SERVER] Executing function for input: '{raw}'")
        
        # Returning the specific message type defined in .proto
        return processor_pb2.ProcessedData(
            output_text=processed,
            character_count=count
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    processor_pb2_grpc.add_DataProcessorServicer_to_server(VisualProcessor(), server)
    server.add_insecure_port('[::]:50051')
    print("Remote Processor is online...")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()