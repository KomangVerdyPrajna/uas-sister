import xmlrpc.client

# The ServerProxy is our Client Stub
proxy = xmlrpc.client.ServerProxy("http://localhost:8000/")

print("Client: Calling 'check_price' remotely...")
# This call triggers the Marshalling process
result = proxy.check_price("laptop")

print(f"Client: The price is ${result}")