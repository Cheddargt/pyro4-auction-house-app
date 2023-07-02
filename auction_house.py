from __future__ import print_function
import time
import Pyro5.api
import threading
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64
import json
import sys

sys.excepthook = Pyro5.errors.excepthook


# define the countup func.
def countupwards():
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("auction.house")
    obj_servidor = Pyro5.api.Proxy(uri)
    t = 1
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        time.sleep(1)
        t += 1
        print(timer, end="\r")
        obj_servidor.updateTimers()

    return 0

# um lance em um produto
# só é adicionado ao objeto do produto se for maior que o lance atual
# deve possuir a chave pública do cliente que o fez
# deve possuir o valor do lance
# deve possuir o nome do cliente que o fez
class Bid(object):
    def __init__(self, clientName, price):
        self.clientName = clientName
        self.price = price

    def getBids(self):
        return self.bids
    
    # pra printar o objeto
    def __str__(self):
        return f"Bidder: {self.name}\nBids: {self.bids}"

class Auction(object):
    def __init__(self, clientRef, code, name, description, initialPrice, endTime):
        self.subscribers = [clientRef]
        self.code = code
        self.name = name
        self.description = description
        self.initialPrice = initialPrice
        self.endTime = endTime
        self.currentBid = initialPrice
        self.currentBidder = None
        self.bids = []

    def newBid(self, price, clientRef):
        client = Pyro5.api.Proxy(clientRef)
        self.currentBid = price
        self.currentBidderRef = clientRef
        self.subscribers.append(clientRef)
        self.bids.append(Bid(client.getName(), price))
        
    def subscribe(self, clientRef):
        self.subscribers.append(clientRef)
        
    def getCode(self):
        return self.code

    def getName(self):
        return self.name
    
    def getInitialPrice(self):
        return self.initialPrice
    
    def getCurrentBid(self):
        return self.currentBid
    
    def getCurrentBidderRef(self):
        return self.currentBidderRef
    
    def getBids(self):
        return self.bids
    
    def getAuctionJson(self):
        return {
            "Código": self.code,
            "Nome": self.name,
            "Lance atual": self.currentBid,
            "Tempo restante": self.endTime,
        }
    
    def getSubscribers(self):
        return self.subscribers
 
    def __str__(self):
        return f"Auction: {self.name}\nStart Price: {self.start_price}\nCurrent Bid: {self.currentBid}\nCurrent Bidder: {self.currentBidder}\nBids: {self.bids}"

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class AuctionHouse(object):
    def __init__(self):
        self.clients = []
        self.auctions = []

    def checkSignature(self, bidder, enc_msg, signature):

        key_path = f'./keys/{bidder}.pem'
        with open('public.pem', 'rb') as f:
            public_key = RSA.import_key(f.read())

        hash = SHA256.new(enc_msg)
        verifier = PKCS1_v1_5.new(public_key)
        is_valid = verifier.verify(hash, signature)
        return is_valid

    def createAuction(self, clientRef, code, name, description, initialPrice, endTime):
        auction = Auction(clientRef, code, name, description, initialPrice, endTime)
        self.auctions.append(auction)
        self.sendNotification("new_auction", auction)
        print("Auction created successfully!")
        return True

    """ res_codes:
    200 = success
    400 = auction not found
    500 = bid lower than current bid
    503 = auction closed
    505 = invalid signature
     """
    def bidAuction (self, clientRef, auctionCode, price, message, signature):
        for auction in self.auctions:
            if auction.getCode() == auctionCode:
                if price > auction.getCurrentBid():
                    if 2>1:
                    # if self.check_signature(bidder, enc_msg, signature):
                        auction.newBid(price, clientRef)
                        print("Bid accepted.")
                        self.sendNotification("new_bid", auction)
                        return 200
                    else:
                        return 505
                else:
                    return 500
            
        return 503
    
    def register(self, nomeCliente, referenciaCliente):

        """
        # string -> b64 -> bytes
        key64 = key64string.encode('utf-8')
        public_key = base64.b64decode(key64)

        # if client with this name exists:
        for client in self.clients:
            if client.name == nomeCliente:
            
                return 500
        client = Pyro5.api.Proxy(referenciaCliente)
        # duas alternativas
        # name = client.getName()
        name = client.name
        # Save public key to a file
        key_path = f'./keys/{name}.pem'
        with open(key_path, 'wb') as f:
            f.write(public_key) 
        """
        for clientRef in self.clients:
            client = Pyro5.api.Proxy(clientRef)
            if client.getName() == nomeCliente:
                return 500

        self.clients.append(referenciaCliente)
        print('cliente adicionado')
        return 200
    
    # atualizar a referencia do cliente no vetor de clientes
    def login(self, nomeCliente, referenciaCliente):
        for clientRef in self.clients:
            client = Pyro5.api.Proxy(clientRef)
            if client.getName() == nomeCliente:
                client.setPyroRef(referenciaCliente)
                return 200
        return 500

    def auctionFinished(self, auction):
        self.sendNotification("auction_finished", auction)
        self.auctions.remove(auction)
        print("Auction finished successfully!")
        return True

    def updateTimers(self):
        for auction in self.auctions:
            auction.endTime -= 1
            if auction.endTime <= 0:
                self.auctionFinished(auction)
    
    def showAuctions(self):
        auctions = []
        if not self.auctions:
            return None
        else:
            for auction in self.auctions:
                auctions.append(auction.getAuctionJson())
            return auctions     
              
    # TODO
    def getBids(self, client_name):
        for client in self.clients:
            if client.name == client_name:
                for auction in self.auctions:
                    for bid in auction.getBids():
                        if bid[1] == client_name:
                            print("Auction:", auction.getName())
                            print("Bid:", bid[0])
                            print("-----------------------------")
                return client.bids
        else:
            print("Client not found.")

    def sendNotification(self, type, auction):
        if (type == "new_auction"):
            for clientRef in self.clients:
                client = Pyro5.api.Proxy(clientRef)
                client.sendMessage("################################")
                client.sendMessage("# [!] new auction has started! #")
                client.sendMessage("################################")
        elif (type == "auction_finished"):
            subscribers = auction.getSubscribers()
            for subRef in subscribers:
                for clientRef in self.clients:

                    client = Pyro5.api.Proxy(clientRef)
                    subscriber = Pyro5.api.Proxy(subRef)
                    currentBidder = Pyro5.api.Proxy(auction.getCurrentBidderRef())

                    if client.getName() == subscriber.getName():
                        client.sendMessage("##########################################")
                        client.sendMessage("##    [!] auction has finished!         ##")
                        client.sendMessage("------------------------------------------")
                        if currentBidder.getName() == subscriber.getName():
                            client.sendMessage("##    [✓] you won bought                ##")
                            client.sendMessage(f' {auction.getName()} for {auction.getCurrentBid()}')
                            client.sendMessage("##########################################")
                        else:
                            client.sendMessage(f'##    [$] {auction.getName()} sold to:')
                            client.sendMessage(f' {currentBidder.getName()} for {auction.getCurrentBid()}')
                            client.sendMessage("##########################################")

        elif (type == "new_bid"):
            subscribers = auction.getSubscribers()
            for subRef in subscribers:
                for clientRef in self.clients:
                    client = Pyro5.api.Proxy(clientRef)
                    subscriber = Pyro5.api.Proxy(subRef)
                    currentBidder = Pyro5.api.Proxy(auction.getCurrentBidderRef())
                    if client.getName() == subscriber.getName():
                        client.sendMessage("################################")
                        client.sendMessage("# [!] a new bid has been made! #")
                        client.sendMessage("--------------------------------")
                        client.sendMessage(f'## item:   {auction.getName()}')
                        client.sendMessage(f'## price:   {auction.getCurrentBid()}')
                        client.sendMessage(f'## client: {currentBidder.getName()}')
                        client.sendMessage("################################")

def main():
 
    daemon = Pyro5.server.Daemon()
    ns = Pyro5.api.locate_ns()
    uri = daemon.register(AuctionHouse)
    ns.register("auction.house", uri)
    print("Auction House is up.")
    
    thread = threading.Thread(target=countupwards, args=())
    print("Timer started.")
    thread.start()

    daemon.requestLoop()
    

if __name__=="__main__":
    main()