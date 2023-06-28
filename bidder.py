from __future__ import print_function
import Pyro4

class Bidder(object):
    def __init__(self, name):
        self.name = name
        self.bids = {}

    def bid(self, auction_house, auction_name, price):
        self.bids[auction_name] = price
        if (auction_house.bid(price, self)):
            print("Bid registered for", auction_name, "at", price)
        else:
            print("Bid not high enough for", auction_name)

    def get_bids(self):
        return self.bids
    
    # this line is only needed if you want to run this as a standalone program
    def __str__(self):
        return f"Bidder: {self.name}\nBids: {self.bids}"
    
    
    

