from __future__ import print_function
import time
import Pyro4
import timer
from Pyro4 import core
import json
import Pyro4
from client import Client
import time
import threading
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64


daemon = Pyro4.Daemon()

# define the countup func.
def countupwards():
    t = 1
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t += 1
        # TODO: adicionar chamada de função que verifica
        auction_house = Pyro4.Proxy("PYRONAME:auction.house")
        auction_house.update_timers()
        print(timer, end="\r")

    return 0

thread = threading.Thread(target=countupwards, args=())
print("Timer started.")
thread.start()

# um lance em um produto
# só é adicionado ao objeto do produto se for maior que o lance atual
# deve possuir a chave pública do cliente que o fez
# deve possuir o valor do lance
# deve possuir o nome do cliente que o fez
class Bid(object):
    def __init__(self, client_name, price):
        self.client_name = client_name
        self.price = price

    def get_bids(self):
        return self.bids
    
    # pra printar o objeto
    def __str__(self):
        return f"Bidder: {self.name}\nBids: {self.bids}"

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
        # TODO: verificar se é melhor name ou client em si
        # RE: é melhor só o nome porque já guardo os clientes registrados na auctionhouse
        self.subscribers = [client_name]

    def new_bid(self, price, bidder_name):
        self.current_bid = price
        self.current_bidder = bidder_name
        self.subscribers.append(bidder_name)
        self.bids.append(Bid(bidder_name, price))
        
    def subscribe(self, client_name):
        # TODO: verificar se é melhor name ou client em si
        # RE: é melhor só o nome porque já guardo os clientes registrados na auctionhouse
        self.subscribers.append(client_name)
        
    def get_code(self):
        return self.code

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
    
    def get_auction_as_json(self):
        return {
            "Código": self.code,
            "Nome": self.name,
            "Lance atual": self.current_bid,
            "Tempo restante": self.end_time,
        }
    
    def get_subscribers(self):
        return self.subscribers
 
    def __str__(self):
        return f"Auction: {self.name}\nStart Price: {self.start_price}\nCurrent Bid: {self.current_bid}\nCurrent Bidder: {self.current_bidder}\nBids: {self.bids}"

## creating an auction house in pyro4
# acessível remotamente
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class AuctionHouse(object):
    def __init__(self):
        self.clients = []
        self.auctions = []

    def create_auction(self, client_name, code, name, description, initial_price, end_time):
        auction = Auction(client_name, code, name, description, initial_price, end_time)
        self.auctions.append(auction)
        # talvez precise alterar pra vetor
        self.send_notification("new_auction", auction)
        print("Auction created successfully!")
        return True

    # register new client to the auction house
    def register(self, name, key64):
        
        message_bytes = base64.b64decode(key64)
        key = message_bytes.decode('ascii')

        # if client with this name exists:
        for client in self.clients:
            if client.name == name:
                return 500
        client = Client(name, key)
        # Save public key to a file
        key_path = f'./keys/{name}.pem'
        with open(key_path, 'wb') as f:
            f.write(key)
        self.clients.append(client)
        return 200
    
    def login(self, name):
        for client in self.clients:
            if client.name == name:
                return 200
        return 500
       
    def update_timers(self):
        for auction in self.auctions:
            auction.end_time -= 1
            if auction.end_time <= 0:
                self.auction_finished(auction)

    def auction_finished(self, auction):
        self.send_notification("auction_finished", auction)
        self.auctions.remove(auction)
        print("Auction finished successfully!")
        return True

    # check existing registration in auction house
    def check_registration(self, name):
        for client in self.clients:
            if client.name == name:
                return True
        return False
    
    def show_auctions(self):
        auctions = []
        # check if there are auctions
        if not self.auctions:
            return None
        else:
            # return json array of auctions
            for auction in self.auctions:
                auctions.append(auction.get_auction_as_json())
            return auctions           

    def check_signature(self, bidder, enc_msg, signature):
        # Load public key from file
        key_path = f'./keys/{bidder}.pem'
        with open('public.pem', 'rb') as f:
            public_key = RSA.import_key(f.read())

        # Verify signature
        # Verify the signature using the public key
        hash = SHA256.new(enc_msg)
        verifier = PKCS1_v1_5.new(public_key)
        is_valid = verifier.verify(hash, signature)
        return is_valid

    # show bids from a specific client
    def get_bids(self, client_name):
        for client in self.clients:
            if client.name == client_name:
                for auction in self.auctions:
                    for bid in auction.get_bids():
                        if bid[1] == client_name:
                            print("Auction:", auction.get_name())
                            print("Bid:", bid[0])
                            print("-----------------------------")
                return client.bids
        else:
            print("Client not found.")

    # allow a client to bid in an auction
    # 200 = success
    # 400 = auction not found
    # 500 = bid lower than current bid
    # 503 = auction closed
    # 505 = invalid signature
    def bid_auction (self, auction_code, price, bidder, enc_msg, signature):
        for auction in self.auctions:
            if auction.get_code() == auction_code:
                if price > auction.get_current_bid():
                    if self.check_signature(bidder, enc_msg, signature):
                        auction.new_bid(price, bidder)
                        print("Bid accepted.")
                        self.send_notification("new_bid", auction)
                        return 200
                    else:
                        return 505
                else:
                    return 500
            
        return 503

    def send_notification(self, type, auction):
        #TODO: notificações pra: leilão criado, lance dado, leilão finalizado
        # enviar notificação pro criador do leilão que o leilão recebeu um novo lance
        # pegar o objeto do cliente pelo pyro proxy
        # acessar o método de notificação do cliente
        # enviar a mensagem
        # quando eu instancio o cliente pelo pyro ele entra no nameserver? vamos ver
            # sim, enquanto ele tá no menu ele está aparecendo no nameserver
            # vamos pegar o proxy do cliente e chamar o método de notificação
        # encontrar o cliente pelo nome usando o pyro4
        if (type == "new_auction"):
            for client in self.clients:
                ns = Pyro4.locateNS()
                uri = ns.lookup(client.name)
                client_obj = Pyro4.Proxy(uri)
                client_obj.send_message("################################")
                client_obj.send_message("# [!] new auction has started! #")
                client_obj.send_message("################################")
        elif (type == "auction_finished"):
            # pode dar problema em referenciar objeto que não tá mais na lista de auctions
            # testado: não deu problema!
            subscribers = auction.get_subscribers()
            for sub in subscribers:
                ns = Pyro4.locateNS()
                uri = ns.lookup(sub)
                client_obj = Pyro4.Proxy(uri)
                client_obj.send_message("##########################################")
                client_obj.send_message("##    [!] auction has finished!         ##")
                client_obj.send_message("------------------------------------------")
                if auction.get_current_bidder() == sub:
                    client_obj.send_message("##    [✓] you won bought                ##")
                    client_obj.send_message(f' {auction.get_name()} for {auction.get_current_bid()}')
                    client_obj.send_message("##########################################")
                else:
                    client_obj.send_message(f'##    [$] {auction.get_name()} sold to:')
                    client_obj.send_message(f' {auction.get_current_bidder()} for {auction.get_current_bid()}')
                    client_obj.send_message("##########################################")
        elif (type == "new_bid"):
            subscribers = auction.get_subscribers()
            for sub in subscribers:
                ns = Pyro4.locateNS()
                uri = ns.lookup(sub)
                client_obj = Pyro4.Proxy(uri)
                client_obj.send_message("################################")
                client_obj.send_message("# [!] a new bid has been made! #")
                client_obj.send_message("--------------------------------")
                client_obj.send_message(f'## item:   {auction.get_name()}')
                client_obj.send_message(f'## price:   {auction.get_current_bid()}')
                client_obj.send_message(f'## client: {auction.get_current_bidder()}')
                client_obj.send_message("################################")



        

def main():

    auction_house = AuctionHouse()

    # not updating timers
    # auction_house.timer_start()

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