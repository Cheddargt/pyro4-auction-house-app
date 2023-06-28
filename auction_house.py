import time
import Pyro4
import timer
from auction import Auction
from Pyro4 import core

class Client(object):
    def __init__(self, name, pubkey, encrypted_password):
        self.name = name
        self.pubkey = pubkey
        self.encrypted_password = encrypted_password
        self.bids = {}

    def bid(self, auction_house, auction_name, price):
        self.bids[auction_name] = price
        if (auction_house.bid(price, self)):
            print("Bid registered for", auction_name, "at", price)
        else:
            print("Bid not high enough for", auction_name)
    
## creating an auction house in pyro4
# acessível remotamente
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class AuctionHouse(object):
    def __init__(self):
        self.clients = []
        self.auctions = []
        # self.events = Pyro4.core.EventDispatcher()

    def create_auction(self, client_name, code, name, description, initial_price, end_time):
        auction = Auction(client_name, code, name, description, initial_price, end_time)
        self.auctions.append(auction)
        self.events.emit("new_auction", name)
    
    def get_auctions(self):
        return self.auctions

    # register new client to the auction house
    def register(self, name, pubkey, encrypted_password):
        if name in self.clients:
            print("Client already registered.")
            return False
        client = Client(name, pubkey, encrypted_password)
        self.clients.append(client)
        

        print("Registro criado com sucesso!")
        return True
    

    # check existing registration in auction house
    def check_registration(self, name):
        return name in self.clients
        
    def show_auctions(self):
        if not self.auctions:
            print("No auctions available.")
        else:
            print("Available Auctions:")
            for auction in self.auctions:
                print("Name:", auction.get_name())
                print("Start Price:", auction.get_start_price())
                print("Current Bid:", auction.get_current_bid())
                print("Current Bidder:", auction.get_current_bidder())
                print("Bids:", auction.get_bids())
                print("-----------------------------")

    # show bids from a specific client
    def show_bids(self, client_name):
        if client_name in self.clients:
            print("Your bids:")
            for auction in self.auctions:
                for bid in auction.get_bids():
                    if bid[1] == client_name:
                        print("Auction:", auction.get_name())
                        print("Bid:", bid[0])
                        print("-----------------------------")
        else:
            print("Client not found.")

    # allow a client to bid in an auction
    def bid_auction (self, auction_name, price, bidder):
        for auction in self.auctions:
            if auction.get_name() == auction_name:
                if auction.bid(price, bidder):
                    # self.events.emit("new_bid", auction_name)
                    # self.events.emit("new_bid", auction_name)
                    print("Bid accepted.")
                    return True
                else:
                    return False
        return False

    def send_notification(self, client_name, message):
        if client_name in self.clients:
            print("Notification sent to", client_name)
            print("Message:", message)
        else:
            print("Client not found.")

    # def subscribe_to_events(self, event, callback):
        # self.events.add_listener(event, callback)

def main():

    auction_house = AuctionHouse()

    def handle_new_auction(auction_name):
        message = f"New auction created: {auction_name}"
        auction_house.send_notification("all", message)

    def handle_new_bid(auction_name):
        message = f"New bid in auction: {auction_name}"
        auction_house.send_notification("all", message)

    def handle_new_client(client_name):
        message = f"New client registered: {client_name}"
        # auction_house.send_notification("all", message)

    # auction_house.subscribe_to_events("new_auction", handle_new_auction)
    # auction_house.subscribe_to_events("new_bid", handle_new_bid)
    # auction_house.subscribe_to_events("new_client", handle_new_client)

    # ns = True. This tells Pyro to use a name server to register 
    # the objects in. (The Pyro4.Daemon.serveSimple is a very easy way 
    # to start a Pyro but it provides very little control
    Pyro4.Daemon.serveSimple(
        {
            AuctionHouse: "auction.house"
        },
        ns = True,
    )

if __name__=="__main__":
    main()