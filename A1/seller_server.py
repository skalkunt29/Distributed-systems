
import socket
import json

# Global Variables
BUFFER_SIZE = 4096
HOST = "127.0.0.1"
PORT = 10001
MAX_WAITING_CONNECTIONS = 200

PRODUCT_DB_HOST = "127.0.0.1"
PRODUCT_DB_PORT = 10002

CUSTOMER_DB_HOST = "127.0.0.1"
CUSTOMER_DB_PORT = 10003


class SellerServer:
    def __init__(self):
        self.logged_users = set()

    def create_seller(self, usr_name, password, name):
        # sql_query = "INSERT INTO CUSTOMER_DB (username, password, name, ...) VALUES (usr_name, password, name, ...); "
        request = {"action": "create_seller", 
                    "username": usr_name,
                    "password": password,
                    "name" : name,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response
    
    def login_seller(self, usr_name, password):
        request = {"action": "login_seller", 
                    "username": usr_name,
                    "password": password,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        if response['success']:
            self.logged_users.add(usr_name)
        return response

    def logout_seller(self, usr_name):
        if usr_name in self.logged_users:
            self.logged_users.remove(usr_name)
        return {"success": True, "message": "user logged out"}
    
    def get_seller_rating(self, usr_name):
        request = {"action": "get_seller_rating", 
                    "username": usr_name}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((CUSTOMER_DB_HOST, CUSTOMER_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response


    def add_item(self, usr_name, item, quantity):
        request = {"action": "add_item", 
                    "username": usr_name,
                    "item" : item,
                    "quantity" : quantity}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((PRODUCT_DB_HOST, PRODUCT_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 


    def remove_item(self, prod_id, quantity):
        request = {"action": "remove_item", 
                    "prod_id": prod_id,
                    "quantity" : quantity}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((PRODUCT_DB_HOST, PRODUCT_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        print(response)
        s.close()
        return response 


    def change_price(self, prod_id, new_price):
        request = {"action": "change_price", 
                    "prod_id": prod_id,
                    "new_price" : new_price}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((PRODUCT_DB_HOST, PRODUCT_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 


    def all_items_by_seller(self, usr_name):
        request = {"action": "all_items_by_seller", 
                    "username": usr_name,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((PRODUCT_DB_HOST, PRODUCT_DB_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 




def handle_request(client_socket, server):
    while True:
        try:
            request_bytes = client_socket.recv(BUFFER_SIZE)
            request = json.loads(request_bytes)
            action = request.get("action")

            if action == "login_seller":
                response = server.login_seller(request.get("username"), request.get("password"))
            elif action == "logout_seller":
                response = server.logout_seller(request.get("username"))

            elif action == "create_seller":
                response = server.create_seller(request.get("username"), request.get("password"), request.get("name"))
            elif action == "get_seller_rating":
                response = server.get_seller_rating(request.get("username"))

            elif action == "add_item":
                response = server.add_item(request.get("username"), request.get("item"), request.get("quantity"))
            elif action == "remove_item":
                response = server.remove_item(request.get("prod_id"), request.get("quantity"))
            elif action == "change_price":
                response = server.change_price(request.get("prod_id"), request.get("new_price"))
            elif action == "all_items_by_seller":
                response = server.all_items_by_seller(request.get("username"))

            else:
                response = {"success": False, "message": "Invalid action"}

            client_socket.sendall(json.dumps(response).encode())
        except:
            client_socket.close()
            return



def start_server():
    
    server = SellerServer()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_WAITING_CONNECTIONS)
    print("=============================")
    print("Server running")
    print("=============================")


    ## Add DUMMY DATA and print FOR TESTING ONLY
    # add_dummy_data(server)
    # test_db(server)

    while True:
        client_socket, client_address = server_socket.accept()
        handle_request(client_socket, server)


    print("=============================")
    print("Server shutdown")
    print("=============================")







##########################################################################
# Testing functions
##########################################################################


##########################################################################

def add_dummy_data(db):

    print("=============================")
    item = {"name": "item1", 
            "category" : 0, 
            "condition" : "new", 
            "keywords" : ("k1", "k2", "k3"), 
            "price" : 100
            }

    request = {"action": "add_item", 
               "username": "usr1",
               "item" : item,
               "quantity" : 2
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
    print(response)



    print("=============================")
    item = {"name": "item2", 
            "category" : 0, 
            "condition" : "new", 
            "keywords" : ("k3", "k4", "k5"), 
            "price" : 100
            }

    request = {"action": "add_item", 
               "username": "usr1",
               "item" : item,
               "quantity" : 2
               }


    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
    print(response)



##########################################################################

def test_db(db):

    print("=============================")

    request = {"action": "remove_item", 
               "prod_id": 0,
               "quantity" : 2, 
               }
    
    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.remove_item(request.get("prod_id"), request.get("quantity"))
    print(response)



    print("=============================")

    request = {"action": "remove_item", 
               "prod_id": 1,
               "quantity" : 1, 
               }
    
    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.remove_item(request.get("prod_id"), request.get("quantity"))
    print(response)




    print("=============================")

    request = {"action": "change_price", 
               "prod_id": 2,
               "new_price" : 50, 
               }
    
    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.change_price(request.get("prod_id"), request.get("new_price"))
    print(response)










##########################################################################

if __name__ == '__main__':
    start_server()






