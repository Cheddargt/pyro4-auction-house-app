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
        obj_servidor.update_timers()

    return 0

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

@Pyro5.api.expose
@Pyro5.api.behavior(instance_mode="single")
class AuctionHouse(object):
    def __init__(self):
        self.clients = []
        self.auctions = []

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

    def create_auction(self, clientRef, code, name, description, initial_price, end_time):
        auction = Auction(clientRef, code, name, description, initial_price, end_time)
        self.auctions.append(auction)
        # talvez precise alterar pra vetor
        self.send_notification("new_auction", auction)
        print("Auction created successfully!")
        return True

    # allow a client to bid in an auction
    """ res_codes:
    200 = success
    400 = auction not found
    500 = bid lower than current bid
    503 = auction closed
    505 = invalid signature
     """
    def bid_auction (self, auction_code, price, bidder, enc_msg, signature):
        for auction in self.auctions:
            if auction.get_code() == auction_code:
                if price > auction.get_current_bid():
                    if 2>1:
                    # if self.check_signature(bidder, enc_msg, signature):
                        auction.new_bid(price, bidder)
                        print("Bid accepted.")
                        self.send_notification("new_bid", auction)
                        return 200
                    else:
                        return 505
                else:
                    return 500
            
        return 503
    
    # register new client to the auction house
    # não passa o objeto do cliente, passa a referência dele
    # referência = uri
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
            f.write(public_key) """
        client = Pyro5.api.Proxy(referenciaCliente)
        self.clients.append(client)
        print('cliente adicionado')
        return 200
    
    # atualizar a referencia do cliente no vetor de clientes
    def login(self, nomeCliente, referenciaCliente):
        for client in self.clients:
            if client.name == nomeCliente:
                # client.pyroRef = referenciaCliente
                return 200
        return 500

    def auction_finished(self, auction):
        self.send_notification("auction_finished", auction)
        self.auctions.remove(auction)
        print("Auction finished successfully!")
        return True

    def update_timers(self):
        for auction in self.auctions:
            auction.end_time -= 1
            if auction.end_time <= 0:
                self.auction_finished(auction)

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
                client.send_message("################################")
                client.send_message("# [!] new auction has started! #")
                client.send_message("################################")
        elif (type == "auction_finished"):
            # pode dar problema em referenciar objeto que não tá mais na lista de auctions
            # testado: não deu problema!
            subscribers = auction.get_subscribers()
            for sub in subscribers:
                for client in self.clients:
                    if client.name == sub:
                        client.send_message("##########################################")
                        client.send_message("##    [!] auction has finished!         ##")
                        client.send_message("------------------------------------------")
                        if auction.get_current_bidder() == sub:
                            client.send_message("##    [✓] you won bought                ##")
                            client.send_message(f' {auction.get_name()} for {auction.get_current_bid()}')
                            client.send_message("##########################################")
                        else:
                            client.send_message(f'##    [$] {auction.get_name()} sold to:')
                            client.send_message(f' {auction.get_current_bidder()} for {auction.get_current_bid()}')
                            client.send_message("##########################################")
        elif (type == "new_bid"):
            subscribers = auction.get_subscribers()
            for sub in subscribers:
                for client in self.clients:
                    if client.name == sub:
                        client.send_message("################################")
                        client.send_message("# [!] a new bid has been made! #")
                        client.send_message("--------------------------------")
                        client.send_message(f'## item:   {auction.get_name()}')
                        client.send_message(f'## price:   {auction.get_current_bid()}')
                        client.send_message(f'## client: {auction.get_current_bidder()}')
                        client.send_message("################################")

def main():
 
    # registra a aplicação do servidor no serviço de nomes
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