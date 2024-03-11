import argparse
import json
import grpc
from concurrent import futures 
import time

from pysyncobj import SyncObj, SyncObjConf, replicated, replicated_sync

from grpc_files import seller_pb2
from grpc_files import seller_pb2_grpc
from grpc_files import buyer_pb2
from grpc_files import buyer_pb2_grpc

from google.protobuf.json_format import Parse, ParseDict, MessageToDict, MessageToJson

from global_variables import *


class DBServer(SyncObj):
    def __init__(self, self_address, other_raft_addresses):
        cfg = SyncObjConf(dynamicMembershipChange = True)
        super(DBServer, self).__init__(self_address, other_raft_addresses, cfg)

        self.prod_id_count = 0

        # stores all items in dict {prod_cat : {prod_id : item_data ... }}
        self.product_data = dict()

        # stores mapping {prod_id : prod_cat}
        self.prod_id_to_cat  = dict()

        # stores seller mapping {usr_name : {set of prod_ids}}
        self.usr_to_prod_id = dict()

        # stores search mapping {keyword : {set of prod_ids}}
        self.search_data = dict()



    def print_DB_state(self):
        print('+' * 40)

        print(self.prod_id_count)

        print("@@@@ product_data @@@@")
        for k, v in self.product_data.items():
            print(k, v)

        print("@@@@ prod_id_to_cat @@@@")
        for k, v in self.prod_id_to_cat.items():
            print(k, v)

        print("@@@@ usr_to_prod_id @@@@")
        for k, v in self.usr_to_prod_id.items():
            print(k, v)

        print("@@@@ search_data @@@@")
        for k, v in self.search_data.items():
            print(k, v)

        print('+' * 40)


    @replicated_sync
    def add_item(self, usr_name, item, quantity):

        prod_cat = item.get("category")
       
        prod_cat = int(prod_cat)
        quantity = int(quantity)

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


    @replicated_sync
    def remove_item(self, prod_id, quantity):
        prod_id = int(prod_id)
        quantity = int(quantity)
        prod_cat = self.prod_id_to_cat.get(prod_id)
        if prod_cat is not None:
            item = self.product_data.get(prod_cat).get(prod_id)
            if item is not None:

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


    @replicated_sync
    def change_price(self, prod_id, new_price):
        prod_id = int(prod_id)
        new_price = int(new_price)
        prod_cat = self.prod_id_to_cat.get(prod_id)

        if prod_cat is not None:
            item = self.product_data.get(prod_cat).get(prod_id)
            if item is not None:
                self.product_data.get(prod_cat).get(prod_id).update({"price" : new_price})

        return {"success": True, "message": "changed item price"}


    @replicated_sync
    def all_items_by_seller(self, usr_name):
        try:
            return {"success": True,
                "items": {id : self.product_data.get(self.prod_id_to_cat.get(id)).get(id) for id in self.usr_to_prod_id.get(usr_name)}}
        except:
            return {"success": False}
    

    @replicated_sync
    def search(self, prod_cat, keywords):

        prod_cat = int(prod_cat)
        if prod_cat not in self.product_data:
            return {"success": True, "items": dict()}
        
        res_ids = set(self.product_data.get(prod_cat).keys())
        for kw in keywords:
            # res_ids = res_ids.intersection(self.search_data.get(kw))
            if kw in self.search_data:
                res_ids = res_ids.union(self.search_data.get(kw))

        if len(res_ids) > 0:
            return {"success": True, "items": {id : self.product_data.get(prod_cat).get(id) for id in res_ids}}

        else:
            return {"success": False}



_g_DB = None


class SellerServicer(seller_pb2_grpc.SellerServicer):
    def __init__(self):
        # self.db = db
        pass
    
    def add_item(self, request, context):
        item = MessageToDict(request.item, including_default_value_fields=True)
        response_dict = _g_DB.add_item(request.username, item, request.quantity)
        response = ParseDict(response_dict, seller_pb2.SellerResponse())
        return response

    def remove_item(self, request, context):
        response_dict = _g_DB.remove_item(request.prod_id, request.quantity)
        response = ParseDict(response_dict, seller_pb2.SellerResponse())
        return response
    
    def change_price(self, request, context):
        response_dict = _g_DB.change_price(request.prod_id, request.new_price)
        response = ParseDict(response_dict, seller_pb2.SellerResponse())
        return response
    
    def all_items_by_seller(self, request, context):
        response_dict = _g_DB.all_items_by_seller(request.username)
        response = ParseDict(response_dict, seller_pb2.SellerItemResponse())
        return response
    


class BuyerServicer(buyer_pb2_grpc.BuyerServicer):
    def __init__(self):
        # self.db = db
        pass

    def search(self, request, context):
        response_dict = _g_DB.search(request.prod_cat, list(request.keywords))
        response = ParseDict(response_dict, buyer_pb2.BuyerItemResponse())
        return response
    
    def all_items_by_seller(self, request, context):
        response_dict = _g_DB.all_items_by_seller(request.username)
        response = ParseDict(response_dict, buyer_pb2.BuyerItemResponse())
        return response
    
    def remove_purchase_item(self, request, context):
        response_dict = _g_DB.remove_item(request.prod_id, request.quantity)
        response = ParseDict(response_dict, buyer_pb2.BuyerResponse())
        return response


def start_server(args):

    node_id = args.node_id
    
    assert node_id < PRODUCT_DB_N, 'max node id PRODUCT_DB_N - 1'

    host, port = PRODUCT_DB_LIST[node_id]

    raft_host, raft_port = PRODUCT_DB_PROTOCOL_LIST[node_id]
    other_raft_addresses = [addr for i, addr in enumerate(PRODUCT_DB_PROTOCOL_LIST[:PRODUCT_DB_N]) if i != node_id]

    # extract host and port from other_raft_addresses
    other_raft_addresses = [addr[0] + ':' + addr[1] for addr in other_raft_addresses]

    # initialize db and server
    global _g_DB
    _g_DB = DBServer(raft_host + ':' + raft_port, other_raft_addresses)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=PRODUCT_DB_MAX_WORKERS))

    # add services to server
    seller_pb2_grpc.add_SellerServicer_to_server(SellerServicer(), server)
    buyer_pb2_grpc.add_BuyerServicer_to_server(BuyerServicer(), server)

    # add port and start server
    server.add_insecure_port(host + ':' + port)
    server.start()

    print("=============================")
    print("Server running")
    print("Server type: PRODUCT DB")
    print("node id:", node_id)
    print(host, port)
    print("RAFT: ", raft_host, raft_port, " >> ", other_raft_addresses)
    print("=============================")

    server.wait_for_termination()

    print("=============================")
    print("Server shutdown")
    print("=============================")







##########################################################################
# Testing functions
##########################################################################


# ##########################################################################

# def add_dummy_data(db):

#     print("=============================")
#     item = {"name": "item1", 
#             "category" : 0, 
#             "condition" : "new", 
#             "keywords" : ("k1", "k2", "k3"), 
#             "price" : 100
#             }

#     request = {"action": "add_item", 
#                "username": "usr1",
#                "item" : item,
#                "quantity" : 2
#                }

#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
#     print(response)



#     print("=============================")
#     item = {"name": "item2", 
#             "category" : 0, 
#             "condition" : "new", 
#             "keywords" : ("k3", "k4", "k5"), 
#             "price" : 100
#             }

#     request = {"action": "add_item", 
#                "username": "usr1",
#                "item" : item,
#                "quantity" : 2
#                }


#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
#     print(response)


#     print("=============================")
#     item = {"name": "item3", 
#             "category" : 0, 
#             "condition" : "new", 
#             "keywords" : ("k3", "k6", "k1"), 
#             "price" : 100
#             }

#     request = {"action": "add_item", 
#                "username": "usr2",
#                "item" : item,
#                "quantity" : 2
#                }

#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
#     print(response)

#     print("=============================")
#     item = {"name": "item4", 
#             "category" : 1, 
#             "condition" : "new", 
#             "keywords" : ("k3", "k1", "k9"), 
#             "price" : 100
#             }

#     request = {"action": "add_item", 
#                "username": "usr2",
#                "item" : item,
#                "quantity" : 2
#                }

#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.add_item(request.get("username"), request.get("item"), request.get("quantity"))
#     print(response)



# ##########################################################################

# def test_db(db):

#     print("=============================")

#     request = {"action": "search", 
#                "category": 0,
#                "keywords" : ("k1", "k3"), 
#                }
    
#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.search(request.get("category"), request.get("keywords"))
#     print(response)


#     print("=============================")

#     request = {"action": "remove_item", 
#                "prod_id": 0,
#                "quantity" : 2, 
#                }
    
#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.remove_item(request.get("prod_id"), request.get("quantity"))
#     print(response)



#     print("=============================")

#     request = {"action": "remove_item", 
#                "prod_id": 1,
#                "quantity" : 1, 
#                }
    
#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.remove_item(request.get("prod_id"), request.get("quantity"))
#     print(response)




#     print("=============================")

#     request = {"action": "change_price", 
#                "prod_id": 2,
#                "new_price" : 50, 
#                }
    
#     # emulate conversion on network
#     request = json.loads(json.dumps(request).encode())
    
#     action = request.get("action")
#     print(action)
#     response = db.change_price(request.get("prod_id"), request.get("new_price"))
#     print(response)








##########################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--node_id', type=int, default=0)
    args = parser.parse_args()

    start_server(args)






