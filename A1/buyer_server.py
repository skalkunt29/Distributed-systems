import socket
import json


#global Variables:
CUSTOMER_DB_HOST="127.0.0.1"
CUSTOMER_DB_PORT=10003
PRODUCT_DB_HOST="127.0.0.1"
PRODUCT_DB_PORT=10002
HOST="127.0.0.1"
PORT=10000
BUFFER_SIZE=4096



class OnlineMarketplace:
    def __init__(self):
        self.logged_users = set()

    def create_account(self, username, password, name):
        request = {"action": "create_buyer", "username": username, "password": password, "name": name}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response
 
    def login(self, username, password):
        request = {"action": "login_buyer", "username": username, "password": password}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        if response['success']:
            self.logged_users.add(usr_name)
        return response
        
    def logout(self, username):
        if username in self.logged_users:
            self.logged_users.remove(username)
        return {"success": True, "message": "user logged out"}

    def add_to_cart(self, username, prod_id, quantity):
        request = {"action": "add_cart", "username": username, "prod_id": prod_id, "quantity": quantity}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response

        

    def view_cart(self, username):
        request = {"action": "display_cart", "username": username}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response

    def clear_cart(self, username):
        request = {"action": "clear_cart", "username": username}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response

    def remove_cart(self, username , prod_id , quantity):
        request = {"action": "display_cart", "username": username, "prod_id":prod_id,"quantity":quantity}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response
        
    def search_items(self, category, keywords):
        request = {"action": "search", "category": category, "keywords":keywords}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response


def handle_client(client_socket, marketplace):
    while True:
        try:
            request_bytes = client_socket.recv(4096)
            request_str = request_bytes
            request = json.loads(request_str)
            action = request.get("action")
            if action == "create_account":
                response = marketplace.create_account(request.get("username"), request.get("password"),request.get("name"))
            elif action == "login":
                response = marketplace.login(request.get("username"), request.get("password"))
            elif action == "logout":
                response = marketplace.logout(request.get("username"))
            elif action == "add_to_cart":
                response = marketplace.add_to_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
            elif action == "remove_cart":
                response = marketplace.add_to_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
            elif action == "view_cart":
                response = marketplace.view_cart(request.get("username"))
            elif action == "clear_cart":
                response = marketplace.view_cart(request.get("username"))    
            elif action == "search_items":
                response = marketplace.search_items(request.get("category"),request.get("keywords"))
            else:
                response = {"success": False, "message": "Invalid action"}
            client_socket.sendall(json.dumps(response).encode())
        except:
            client_socket.close()
            return


def start_server():
    marketplace = OnlineMarketplace()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST,PORT))
    server_socket.listen()
    print("Server started")
    while True:
        client_socket, client_address = server_socket.accept()
        handle_client(client_socket, marketplace)


start_server()