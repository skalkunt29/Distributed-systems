
import socket
import json

# Global Variables
BUFFER_SIZE = 4096
HOST = "127.0.0.1"
PORT = 10003
MAX_WAITING_CONNECTIONS = 200


class DBServer:
    def __init__(self):
        self.seller_id_count = 0
        self.seller_data  = dict()

        self.buyer_id_count = 0
        self.buyer_data = dict()

        self.cart_data = dict()


    def create_seller(self, usr_name, password, name):
        if usr_name in self.seller_data:
            return {"success": False, "message": "username not available"}
        
        self.seller_data.update({usr_name : 
                                 {"password" : password, 
                                  "id" :  self.seller_id_count, 
                                  "name" : name,
                                  "feedback_pos" : 0,
                                  "feedback_neg" : 0,
                                  "num_items_sold" : 0
                                  }})
        self.seller_id_count += 1
        return {"success": True, "message": "Account created successfully"}
    
    
    def login_seller(self, usr_name, password):
        if usr_name in self.seller_data and self.seller_data.get(usr_name).get("password") == password:
            return {"success": True, "message": "credentials verified"}
        
        return {"success": False, "message": "wrong username or password"}

    def get_seller_rating(self, usr_name):
        if usr_name in self.seller_data:
            return {"success": True, 
                    "rating_pos" : self.seller_data.get("feedback_pos"), 
                    "rating_neg" : self.seller_data.get("feedback_neg")}
        
        return {"success": False, "message": "username does not exist"}

    def create_buyer(self, usr_name, password, name):
        if usr_name in self.buyer_data:
            return {"success": False, "message": "username not available"}
        
        self.buyer_data.update({usr_name : 
                                 {"password" : password, 
                                  "id" :  self.buyer_id_count, 
                                  "name" : name,
                                  "num_items_purchased" : 0
                                  }})
        self.buyer_id_count += 1
        return {"success": True, "message": "Account created successfully"}
    
    
    def login_buyer(self, usr_name, password):
        if usr_name in self.buyer_data and self.buyer_data.get(usr_name).get("password") == password:
            return {"success": True, "message": "credentials verified"}
        
        return {"success": False, "message": "wrong username or password"}
    

    def add_cart(self, usr_name, prod_id, quantity):
        if usr_name in self.cart_data:
            self.cart_data[usr_name].update({prod_id : quantity})
        else:
            self.cart_data[usr_name] = dict({prod_id : quantity})

        return {"success": True, "message": "item added to cart"}
    
    def remove_cart(self, usr_name, prod_id, quantity):
        if usr_name in self.cart_data and prod_id in self.cart_data.get(usr_name):
            new_quantity = self.cart_data.get(usr_name).get(prod_id) - quantity

            if new_quantity > 0:
                self.cart_data[usr_name].update({prod_id : new_quantity})
            else:
                self.cart_data[usr_name].pop(prod_id)
                if len(self.cart_data[usr_name]) == 0:
                    self.clear_cart(usr_name)

            return {"success": True, "message": "item removed from cart"}
        
        return {"success": False, "message": "invalid product id / username"}

    def clear_cart(self, usr_name):
        if usr_name in self.cart_data:
            self.cart_data.pop(usr_name)
        return {"success": True, "message": "cart cleared"}

    def display_cart(self, usr_name):
        if usr_name in self.cart_data:
            return {"success": True, "cart": self.cart_data.get(usr_name)}
        return {"success": False, "message": "no cart found"}



def handle_request(client_socket, db):
    while True:
        try:
            request_bytes = client_socket.recv(BUFFER_SIZE)
            request = json.loads(request_bytes)
            action = request.get("action")

            if action == "login_seller":
                response = db.login_seller(request.get("username"), request.get("password"))
            elif action == "login_buyer":
                response = db.login_buyer(request.get("username"), request.get("password"))

            elif action == "create_seller":
                response = db.create_seller(request.get("username"), request.get("password"), request.get("name"))
            elif action == "create_buyer":
                response = db.create_buyer(request.get("username"), request.get("password"), request.get("name"))

            elif action == "add_cart":
                response = db.add_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
            elif action == "remove_cart":
                response = db.remove_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
            elif action == "clear_cart":
                response = db.clear_cart(request.get("username"))
            elif action == "display_cart":
                response = db.display_cart(request.get("username"))

            elif action == "get_seller_rating":
                response = db.get_seller_rating(request.get("username"))

            else:
                response = {"success": False, "message": "Invalid action"}

            client_socket.sendall(json.dumps(response).encode())
        except:
            client_socket.close()
            return




def start_server():
    
    db = DBServer()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_WAITING_CONNECTIONS)
    print("=============================")
    print("Server running")
    print("=============================")


    ## Add DUMMY DATA and print FOR TESTING ONLY
    # add_dummy_data(db)
    # print_db_state(db)
    # test_db(db)
    # print_db_state(db)


    while True:
        client_socket, client_address = server_socket.accept()
        handle_request(client_socket, db)


    print("=============================")
    print("Server shutdown")
    print("=============================")










##########################################################################
# Testing functions
##########################################################################

def print_db_state(db):
    print("=============================")
    print(db.seller_id_count)
    print("=============================")
    for k, v in db.seller_data.items():
        print(k, v)

    print("=============================")
    print(db.buyer_id_count)

    print("=============================")
    for k, v in db.buyer_data.items():
        print(k, v)

    print("=============================")
    for k, v in db.cart_data.items():
        print(k, v)



##########################################################################


def add_dummy_data(db):

    print("=============================")

    request = {"action": "create_seller", 
               "username": "usr1",
               "password": "pw1",
               "name" : "name1",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_seller(request.get("username"), request.get("password"), request.get("name"))
    print(response)

    print("=============================")

    request = {"action": "create_seller", 
               "username": "usr2",
               "password": "pw2",
               "name" : "name2",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_seller(request.get("username"), request.get("password"), request.get("name"))
    print(response)

    print("=============================")

    request = {"action": "create_seller", 
               "username": "usr2",
               "password": "pw2",
               "name" : "name2",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_seller(request.get("username"), request.get("password"), request.get("name"))
    print(response)




    print("=============================")

    request = {"action": "create_buyer", 
               "username": "usr4",
               "password": "pw4",
               "name" : "name4",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_buyer(request.get("username"), request.get("password"), request.get("name"))
    print(response)


    print("=============================")

    request = {"action": "create_buyer", 
               "username": "usr5",
               "password": "pw5",
               "name" : "name5",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_buyer(request.get("username"), request.get("password"), request.get("name"))
    print(response)


    print("=============================")

    request = {"action": "create_buyer", 
               "username": "usr5",
               "password": "pw5",
               "name" : "name5",
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.create_buyer(request.get("username"), request.get("password"), request.get("name"))
    print(response)


##########################################################################


def test_db(db):
    

    print("=============================")

    request = {"action": "add_cart", 
               "username": "usr5",
               "prod_id": 1,
               "quantity" : 3,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.add_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
    print(response)


    print("=============================")

    request = {"action": "add_cart", 
               "username": "usr5",
               "prod_id": 2,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.add_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
    print(response)


    print("=============================")

    request = {"action": "add_cart", 
               "username": "usr5",
               "prod_id": 3,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.add_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
    print(response)


    print("=============================")

    request = {"action": "remove_cart", 
               "username": "usr5",
               "prod_id": 3,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.remove_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
    print(response)



    print("=============================")

    request = {"action": "remove_cart", 
               "username": "usr5",
               "prod_id": 1,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.remove_cart(request.get("username"), request.get("prod_id"), request.get("quantity"))
    print(response)




    print("=============================")

    request = {"action": "display_cart", 
               "username": "usr5",
               "prod_id": 1,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.display_cart(request.get("username"))
    print(response)




    print("=============================")

    request = {"action": "clear_cart", 
               "username": "usr5",
               "prod_id": 1,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.clear_cart(request.get("username"))
    print(response)



    print("=============================")

    request = {"action": "display_cart", 
               "username": "usr5",
               "prod_id": 1,
               "quantity" : 1,
               }

    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.display_cart(request.get("username"))
    print(response)








##########################################################################

if __name__ == '__main__':
    start_server()






