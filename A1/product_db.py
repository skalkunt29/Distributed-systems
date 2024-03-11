
import socket
import json

# Global Variables
BUFFER_SIZE = 4096
HOST = "127.0.0.1"
PORT = 10002
MAX_WAITING_CONNECTIONS = 200


class DBServer:
    def __init__(self):
        self.prod_id_count = 0

        # stores all items in dict {prod_cat : {prod_id : item_data ... }}
        self.product_data = dict()

        # stores mapping {prod_id : prod_cat}
        self.prod_id_to_cat  = dict()

        # stores seller mapping {usr_name : {set of prod_ids}}
        self.usr_to_prod_id = dict()

        # stores search mapping {keyword : {set of prod_ids}}
        self.search_data = dict()
        

    def add_item(self, usr_name, item, quantity):

        prod_cat = item.get("category")
        item.update({"sold_by" : usr_name})
        item.update({"quantity" : quantity})

        # update entire db state
        if prod_cat in self.product_data:
            self.product_data[prod_cat].update({self.prod_id_count : item})
        else:
            self.product_data[prod_cat] = dict({self.prod_id_count : item})
        
        # always unique key
        self.prod_id_to_cat.update({self.prod_id_count : prod_cat})
        
        if usr_name in self.usr_to_prod_id:
            self.usr_to_prod_id[usr_name].add(self.prod_id_count)
        else:
            self.usr_to_prod_id[usr_name] = set({self.prod_id_count})

        for kw in item.get("keywords"):
            if kw in self.search_data:
                self.search_data[kw].add(self.prod_id_count)
            else:
                self.search_data[kw] = set({self.prod_id_count})

        # update id counter
        self.prod_id_count += 1
        return {"success": True, "message": "item successfully added!"}


    def remove_item(self, prod_id, quantity):
        prod_cat = self.prod_id_to_cat.get(prod_id)
        if prod_cat:
            item = self.product_data.get(prod_cat).get(prod_id)
            if item:

                new_quantity = item.get("quantity") - quantity

                if new_quantity > 0:
                    self.product_data.get(prod_cat).get(prod_id).update({"quantity" : new_quantity})
                else:
                    self.product_data.get(prod_cat).pop(prod_id)
                    self.prod_id_to_cat.pop(prod_id)
                    self.usr_to_prod_id.get(item.get("sold_by")).remove(prod_id)
                    for kw in item.get("keywords"):
                        self.search_data.get(kw).remove(prod_id)
                
        return {"success": True, "message": "removed item from DB"}


    def change_price(self, prod_id, new_price):
        prod_cat = self.prod_id_to_cat.get(prod_id)
        self.product_data.get(prod_cat).get(prod_id).update({"price" : new_price})
        return {"success": True, "message": "changed item price"}


    def all_items_by_seller(self, usr_name):
        return {"success": True,
                "items": {id : self.product_data.get(self.prod_id_to_cat.get(id)).get(id) for id in self.usr_to_prod_id.get(usr_name)}}
    

    def search(self, prod_cat, keywords):
        res_ids = set(self.product_data.get(prod_cat).keys())
        for kw in keywords:
            res_ids = res_ids.intersection(self.search_data.get(kw))
        return {"success": True, "items": {id : self.product_data.get(prod_cat).get(id) for id in res_ids}}



def handle_request(client_socket, db):
    while True:
        try:
            request_bytes = client_socket.recv(BUFFER_SIZE)
            request = json.loads(request_bytes)
            action = request.get("action")

            if action == "search":
                response = db.search(request.get("category"), request.get("keywords"))

            elif action == "add_item":
                response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
            elif action == "remove_item":
                response = db.remove_item(request.get("prod_id"), request.get("quantity"))

            elif action == "change_price":
                response = db.change_price(request.get("prod_id"), request.get("new_price"))
            elif action == "all_items_by_seller":
                response = db.all_items_by_seller(request.get("username"))

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
    print(db.prod_id_count)
    print("=============================")
    for k, v in db.product_data.items():
        for k1, v1 in v.items():
            print(k, k1, v1)
    print("=============================")
    for k, v in db.prod_id_to_cat.items():
        print(k, v)
    print("=============================")
    for k, v in db.usr_to_prod_id.items():
        print(k, v)
    print("=============================")
    for k, v in db.search_data.items():
        print(k, v)
    print("=============================")



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


    print("=============================")
    item = {"name": "item3", 
            "category" : 0, 
            "condition" : "new", 
            "keywords" : ("k3", "k6", "k1"), 
            "price" : 100
            }

    request = {"action": "add_item", 
               "username": "usr2",
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
    item = {"name": "item4", 
            "category" : 1, 
            "condition" : "new", 
            "keywords" : ("k3", "k1", "k9"), 
            "price" : 100
            }

    request = {"action": "add_item", 
               "username": "usr2",
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

    request = {"action": "search", 
               "category": 0,
               "keywords" : ("k1", "k3"), 
               }
    
    # emulate conversion on network
    request = json.loads(json.dumps(request).encode())
    
    action = request.get("action")
    print(action)
    response = db.search(request.get("category"), request.get("keywords"))
    print(response)


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






