import time
import Pyro4
import timer

class Auction(object):
    # Prompt clients to provide product code, name, description, initial price, and auction end time.
    def __init__(self, client_name, code, name, description, initial_price, end_time):
        self.code = code
        self.name = name
        self.description = description
        self.initial_price = initial_price
        self.end_time = end_time
        self.current_bid = initial_price
        self.current_bidder = None
        self.bids = []
        self.subscribers = [client_name]
        self.timer = timer.start(end_time, self.auction_finished)
        

    def bid(self, price, bidder):
        if price > self.current_bid:
            self.current_bid = price
            self.current_bidder = bidder
            self.subscribers.append(bidder)
            self.bids.append((price, bidder))
            return True
        else:
            return False
        
    def subscribe(self, client_name):
        self.subscribers.append(client_name)
        
    def get_name(self):
        return self.name
    
    def get_initial_price(self):
        return self.initial_price
    
    def get_current_bid(self):
        return self.current_bid
    
    def get_current_bidder(self):
        return self.current_bidder
    
    def get_bids(self):
        return self.bids
    
    def auction_finished(self):
        return self.timer.finished()
    
    def get_subscribers(self):
        return self.subscribers
 
    def __str__(self):
        return f"Auction: {self.name}\nStart Price: {self.start_price}\nCurrent Bid: {self.current_bid}\nCurrent Bidder: {self.current_bidder}\nBids: {self.bids}"
