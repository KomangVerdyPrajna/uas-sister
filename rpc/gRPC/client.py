import grpc
import processor_pb2
import processor_pb2_grpc

def run_client():
    # Connect to the remote server
    with grpc.insecure_channel('localhost:50051') as channel:
        # Instantiate the Stub (The Proxy)
        stub = processor_pb2_grpc.DataProcessorStub(channel)
        
        # User Input
        user_input = "python rpc is powerful"
        
        # Execute the remote function!
        print(f"[CLIENT] Requesting transformation for: '{user_input}'")
        request = processor_pb2.RawData(input_text=user_input)
        
        # The call happens here
        response = stub.TransformText(request)
        
        print(f"[CLIENT] Result: {response.output_text}")
        print(f"[CLIENT] Count: {response.character_count}")

if __name__ == "__main__":
    run_client()