**This demonstration utilizes the [gRPC framework](https://grpc.io/) for remote procedure call (RPC) implementation. gRPC handles underlying network communication internally, allowing developers to concentrate primarily on business logic.**<br><br>
To use this demo, follow steps below:
1. Create a new python environment:<br>
    ``` python -m venv myenv ```
2. Execute:<br>
    ``` myenv\Scripts\activate ``` 
    Or, in VS Code, click Ctrl+Shift+P --> Python: Select Interpreter, choose an environment
3. Install dependencies<br>
    ```  pip install -r requirements.txt ``` 
4. Define the contract file:<br>
    processor.proto
5. Execute:<br>
    ``` python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. processor.proto ```
    It will create the stub files:
    - processor_pb2_grpc.py
    - processor_pb2.py
6. Run:<br>
    ```
    python server.py
    python client.py
    ```

