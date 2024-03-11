
import socket
import json
import time


# Global Variables
BUFFER_SIZE = 4096

SELLER_SERVER_HOST = "127.0.0.1"
SELLER_SERVER_PORT = 10001



class SellerClient:
    def __init__(self):
        self.logged_users = set()
        
    def create_seller(self, usr_name, password, name):
        # sql_query = "INSERT INTO CUSTOMER_DB (username, password, name, ...) VALUES (usr_name, password, name, ...); "
        request = {"action": "create_seller", 
                    "username": usr_name,
                    "password": password,
                    "name" : name,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response
    
    def login_seller(self, usr_name, password):
        request = {"action": "login_seller", 
                    "username": usr_name,
                    "password": password,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        if response['success']:
            self.logged_users.add(usr_name)
        return response

    def logout_seller(self, usr_name):
        request = {"action": "logout_seller", 
                    "username": usr_name}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response
    
    def get_seller_rating(self, usr_name):
        request = {"action": "get_seller_rating", 
                    "username": usr_name}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
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
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 


    def remove_item(self, prod_id, quantity):
        request = {"action": "remove_item", 
                    "prod_id": prod_id,
                    "quantity" : quantity}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())

        print(request)


        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 


    def change_price(self, prod_id, new_price):
        request = {"action": "change_price", 
                    "prod_id": prod_id,
                    "new_price" : new_price}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 


    def all_items_by_seller(self, usr_name):
        request = {"action": "all_items_by_seller", 
                    "username": usr_name,}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SELLER_SERVER_HOST, SELLER_SERVER_PORT))
        s.sendall(json.dumps(request).encode())
        response = json.loads(s.recv(BUFFER_SIZE))
        s.close()
        return response 



def start_client():
    
    client = SellerClient()



    ## Add DUMMY DATA and print FOR TESTING ONLY
    # add_dummy_data(client)
    # test_db(client)

    start_time = time.time()

    max_iterations = 100



    # for i in range(max_iterations):
        
    #     request = {"action": "create_seller", 
    #             "username": "usr" + str(i),
    #             "password": "pw" + str(i),
    #             "name" : "name" + str(i),
    #             }

    #     # emulate conversion on network
    #     request = json.loads(json.dumps(request).encode())
    #     response = client.create_seller(request.get("username"), request.get("password"), request.get("name"))


    # print(time.time() - start_time)


    for i in range(max_iterations):
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
        response = client.add_item(request.get("username"), request.get("item"), request.get("quantity"))
        #print(response)

    print((time.time() - start_time)/100)









##########################################################################
# Testing functions
##########################################################################


##########################################################################




##########################################################################

if __name__ == '__main__':
    
    start_client()






