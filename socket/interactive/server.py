import socket
import threading

HOST = "127.0.0.1"
PORT = 12345
clients = {} # Dictionary: { "Client-ID": socket_object }
counter = 1

DATA_SIZE = 1024

def update_console():
    """Refreshes the server view of active clients."""
    print("\n" + "="*30)
    print(f"ACTIVE CLIENTS: {list(clients.keys())}")
    print("="*30 + "\n")

def handle_client(conn, addr, client_id):
    print(f"[LOG] {client_id} joined from {addr}")
    
    while True:
        try:
            data = conn.recv(DATA_SIZE).decode('utf-8')
            if not data or data.lower() == 'exit':
                break
            
            # Expected format: "TargetID:Message"
            if ":" in data:
                target_id, message = data.split(":", 1)
                target_id = target_id.strip()
                
                if target_id in clients:
                    # The Server monitors the DM
                    print(f"[SPY] {client_id} -> {target_id}: {message}")
                    clients[target_id].send(f"[{client_id}]: {message}".encode('utf-8'))
                else:
                    conn.send(f"SERVER: Client {target_id} not found.".encode('utf-8'))
            else:
                conn.send("SERVER: Use format 'ID:Message'".encode('utf-8'))
                
        except:
            break

    # Cleanup
    print(f"[DISCONNECT] {client_id} left.")
    del clients[client_id]
    conn.close()
    update_console()

def start_server():
    global counter
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server Monitoring Station active on {PORT}...")

    while True:
        conn, addr = server.accept()
        client_id = f"Client-{counter}"
        clients[client_id] = conn
        counter += 1
        
        update_console()
        
        # Tell the client what their ID is
        conn.send(f"ID:{client_id}".encode('utf-8'))
        
        thread = threading.Thread(target=handle_client, args=(conn, addr, client_id))
        thread.start()

if __name__ == "__main__":
    start_server()