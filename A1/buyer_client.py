import socket
import json
import time
BUYER_SERVER_HOST="127.0.0.1"
BUYER_SERVER_PORT=10000

class Client:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((BUYER_SERVER_HOST,BUYER_SERVER_PORT))
    
    def create_account(self, username, password, name):
        request = {"action": "create_account", "username": username, "password": password, "name":name}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response

    def login(self, username, password):
        request = {"action": "login", "username": username, "password": password}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        if response["success"]:
            self.logged_in = True
            self.username = username
        return response

    def logout(self):
        if not self.logged_in:
            return {"success": False, "message": "Not logged in"}
        request = {"action": "logout", "username": self.username}
        self.client_socket.sendall(json.dumps(request).encode)
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        if response["success"]:
            self.logged_in = False
            self.username = None
        return response

    def add_to_cart(self, prod_id, quantity):
        if not self.logged_in:
            return {"success": False, "message": "Not logged in"}
        request = {"action": "add_to_cart", "username": self.username, "prod_id": prod_id, "quantity": quantity}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response

    def remove_cart(self, prod_id, quantity):
        if not self.logged_in:
            return {"success": False, "message": "Not logged in"}
        request = {"action": "add_to_cart", "username": self.username, "prod_id": prod_id, "quantity": quantity}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response

    def view_cart(self):
        if not self.logged_in:
            return {"success": False, "message": "Not logged in"}
        request = {"action": "view_cart", "username": self.username}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response

    def clear_cart(self):
        if not self.logged_in:
            return {"success": False, "message": "Not logged in"}
        request = {"action": "clear_cart", "username": self.username}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response

    def search_items(self, category, keywords):
        request = {"action": "search_items", "category": category,"keywords":keywords}
        self.client_socket.sendall(json.dumps(request).encode())
        response_bytes = self.client_socket.recv(4096)
        response = json.loads(response_bytes)
        return response



total_time=0
iterations=1000
client = Client()

for i in range(iterations):
    start_time=time.time()
    response = client.create_account("username"+str(iterations), "password"+str(iterations), "name"+str(iterations))
    end_time=time.time()
    total_time+=end_time-start_time
    
    
average_response_time=total_time/iterations
print(average_response_time)