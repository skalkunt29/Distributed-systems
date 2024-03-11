
CSCI 5673 Distributed Systems programming assignment 1

Nikhil Barhate and Sriranga Kalkunte Ramaswamy


Design aspects:

    1. Communication between any 2 services is achieved by a TCP connection.
    2. Data is formated as JSON objects, serialized to a string of bytes for communication via TCP.
    3. All response messages contain a boolean variable ('success') to determine the status of the request.
    6. login sessions are stored on the servers.
    4. The product and customer databases run on separate services to emulate the existance of separate databases.
    5. The data is stored in memory on these separate services in the form of nested python dictionaries.
    7. The search function is implemented as follows:
        - input: product category and keywords (Given Design Spec)
        - output: list of all the matching items
        - we maintain a dictionary (search_data) that maps keyword => set of product ids
        - we first get a set of all the product ids of the given product category
        - then we get a set of product ids associated with all of the keywords by 
            intersecting product id sets associated with each of the given keyword (stored in search_data)
        - then we calculate the intersection of these 2 sets to get our final search results.


Assumptions:

    - for the search function, the keywords in the database exactly match the keywords in the query
    - while removing an item if updated quantity is less than or equal to 0, then the item is removed from the database
    - while viewing the cart the buyer can see product ids only, rest of the product characterstics 
        can be refered from results of the search query.


Things that work:

    - seller side:
        - create a new seller account
        - login / logout a seller account
        - get seller rating
        - put an item for sale 
        - change the sale price of an item
        - remove and item from sale 
        - display items currently on sale
    
    - buyer side:
        - create a new buyer account 
        - login / logout a buyer account 
        - search items for sale 
        - add item to cart 
        - remove item from cart 
        - clear cart 
        - display cart 


Things that do not work:

    - Little to no exception handling
    - provide feedback (requires make purchase)
    - get buyer purchase history (requires make purchase)






