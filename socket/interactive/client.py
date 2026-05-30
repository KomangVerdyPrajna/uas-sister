import socket
import threading

HOST = "127.0.0.1"
PORT = 12345
DATA_SIZE = 1024

def receive_messages(s):
    while True:
        try:
            msg = s.recv(DATA_SIZE).decode('utf-8')
            print(f"\n{msg}\nSend to (ID:Message): ", end="")
        except:
            break

def start_client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # First message from server is our ID
    init_msg = s.recv(DATA_SIZE).decode('utf-8')
    if init_msg.startswith("ID:"):
        my_id = init_msg.split(":")[1]
        print(f"--- YOUR IDENTITY: {my_id} ---")

    threading.Thread(target=receive_messages, args=(s,), daemon=True).start()

    print("Instructions: Type 'Client-X:Hello' to talk to someone.")
    while True:
        target_and_msg = input("Send to (ID:Message): ")
        if target_and_msg.lower() == 'quit':
            break
        s.send(target_and_msg.encode('utf-8'))

    s.close()

if __name__ == "__main__":
    start_client()