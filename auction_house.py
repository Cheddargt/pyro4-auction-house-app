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
daemon = Pyro5.server.Daemon()


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
    def __init__(self, itemName, itemCode, clientName, price):
        self.itemName = itemName
        self.itemCode = itemCode
        self.clientName = clientName
        self.price = price

    def getItemName(self):
        return self.itemName
    
    def getItemCode(self):
        return self.itemCode
    
    def getClientName(self):
        return self.clientName
    
    def getPrice(self):
        return self.price
    
    # pra printar o objeto
    def __str__(self):
        return f"Bidder: {self.name}\nBids: {self.bids}"

class Auction(object):
    def __init__(self, clientName, code, name, description, initialPrice, endTime):
        self.subscribers = [clientName]
        self.code = code
        self.name = name
        self.description = description
        self.initialPrice = initialPrice
        self.endTime = endTime
        self.currentBid = initialPrice
        self.currentBidder = ''
        self.bids = []

    def newBid(self, price, clientName):
        self.currentBid = price
        self.subscribers.append(clientName)
        self.bids.append(Bid(self.name, self.code, clientName, price))
        self.currentBidder = clientName
        
    def subscribe(self, clientName):
        self.subscribers.append(clientName)
        
    def getCode(self):
        return self.code

    def getName(self):
        return self.name
    
    def getInitialPrice(self):
        return self.initialPrice
    
    def getCurrentBid(self):
        return self.currentBid
    
    def getCurrentBidder(self):
        return self.currentBidder
    
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

class ClienteServidor(object):
    def __init__(self, name, pyroRef):
        self.name = name
        self.pyroRef = pyroRef
  
    def setPyroRef(self, newRef):
        self.pyroRef = newRef

    def getPyroRef(self):
        return self.pyroRef
        
    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name 



@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class AuctionHouse(object):
    def __init__(self):
        self.listaClientes = []
        self.auctions = []

    def checkSignature(self, bidder, enc_msg, signature):

        key_path = f'./keys/{bidder}.pem'
        with open('public.pem', 'rb') as f:
            public_key = RSA.import_key(f.read())

        hash = SHA256.new(enc_msg)
        verifier = PKCS1_v1_5.new(public_key)
        is_valid = verifier.verify(hash, signature)
        return is_valid

    def createAuction(self, clientName, code, name, description, initialPrice, endTime):

        auction = Auction(clientName, code, name, description, initialPrice, endTime)
        self.auctions.append(auction)
        self.sendNotification("new_auction", auction)
        return True

    """ res_codes:
    200 = success
    400 = auction not found
    500 = bid lower than current bid
    503 = auction closed
    505 = invalid signature
     """
    def bidAuction (self, clientName, auctionCode, price, message, signature):
        for auction in self.auctions:
            if auction.getCode() == auctionCode:
                if price > auction.getCurrentBid():
                    # TODO:
                    # if self.check_signature(bidder, enc_msg, signature):
                    if 2>1:
                        auction.newBid(price, clientName)
                        for clienteServidor in self.listaClientes:
                            if clientName == clienteServidor.getName():
                                client = Pyro5.api.Proxy(clienteServidor.getPyroRef())
                                client.addBid(auction.getName(), auctionCode, price)

                        # notificar subscribers que um novo lance foi feito
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
        for clienteServidor in self.listaClientes:
            if clienteServidor.getName() == nomeCliente:
                return 500

        self.listaClientes.append(ClienteServidor(nomeCliente, referenciaCliente))
        return 200
    
    # atualizar a referencia do cliente na lista do servidor
    def login(self, nomeCliente, referenciaCliente):
        for clienteServidor in self.listaClientes:
            if clienteServidor.name == nomeCliente:
                clienteServidor.pyroRef = referenciaCliente
                return 200
        return 500

    def auctionFinished(self, auction):
        self.sendNotification("auction_finished", auction)
        self.auctions.remove(auction)
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
     
    def getBids(self, clientName):
        for clienteServidor in self.listaClientes:
            if clienteServidor.getName() == clientName:
                client = Pyro5.api.Proxy(clienteServidor.getPyroRef())
                clientBids = client.getBids()
                if clientBids == []:
                    return (None)
                return (clientBids)


    def sendNotification(self, type, auction):

        if (type == "new_auction"):
            for clienteServidor in self.listaClientes:
                client = Pyro5.api.Proxy(clienteServidor.pyroRef)
                client.sendMessage("###########################################################")
                client.sendMessage("<<<<<<<<<<<<< [!] new auction has started! >>>>>>>>>>>>>>>>")
                client.sendMessage("###########################################################")

        elif (type == "auction_finished"):
            subscribers = auction.getSubscribers()
            currentBidderName = auction.getCurrentBidder()
            for subscriberName in subscribers:
                for clienteServidor in self.listaClientes:
                    client = Pyro5.api.Proxy(clienteServidor.getPyroRef())

                    if clienteServidor.getName() == subscriberName:
                        client.sendMessage("###########################################################")
                        client.sendMessage("##    [!] auction has finished!         ###################")
                        client.sendMessage("-----------------------------------------------------------")
                        if currentBidderName == subscriberName:
                            client.sendMessage("##    [✓] you bought                ##################")
                            client.sendMessage(f'## {auction.getName()} for {auction.getCurrentBid()}')
                            client.sendMessage("###########################################################")
                        else:
                            client.sendMessage(f'##    [$] {auction.getName()} sold to:')
                            client.sendMessage(f'## {currentBidderName} for {auction.getCurrentBid()}')
                            client.sendMessage("###########################################################")

        elif (type == "new_bid"):
            subscribers = auction.getSubscribers()
            currentBidderName = auction.getCurrentBidder()
            for subscriberName in subscribers:
                for clienteServidor in self.listaClientes:
                    client = Pyro5.api.Proxy(clienteServidor.getPyroRef())

                    # TODO: clienteServidor.name == ...
                    if clienteServidor.getName() == subscriberName:
                        client.sendMessage("###########################################################")
                        client.sendMessage("# [!] a new bid has been made! #")
                        client.sendMessage("-----------------------------------------------------------")
                        client.sendMessage(f'## item:   {auction.getName()}')
                        client.sendMessage(f'## price:   {auction.getCurrentBid()}')
                        client.sendMessage(f'## client: {currentBidderName}')
                        client.sendMessage("###########################################################")

def main():
 
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