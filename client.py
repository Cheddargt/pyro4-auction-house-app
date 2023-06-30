import Pyro4

# Define the client class
# (object) is the superclass of all classes in Python
@Pyro4.expose
class Client(object):
    def __init__(self, name, pubkey):
        self.name = name
        self.pubkey = pubkey
        self.bids = {}


    def send_message(self, message):
        print(message)

    # pra printar o objeto
    def __str__(self):
        return f"Name: {self.name}\nBids: {self.bids}"