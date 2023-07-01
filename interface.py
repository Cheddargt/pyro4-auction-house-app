import sys
import Pyro4
import Pyro4.util
from client import Client
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
global client_name
global uri
global pubkey
import threading
import base64
import Pyro5.api
import threading

daemon = Pyro5.server.Daemon()


class Client(object):
    def __init__(self, name):
        self.name = name
        self.bids = {}

    @Pyro5.api.expose
    @Pyro5.api.callback
    def send_message(self, message):
        print(message)

    def loopThread(daemon):
        daemon.requestLoop()

    # pra printar o objeto
    def __str__(self):
        return f"Name: {self.name}\nBids: {self.bids}"

def get_signature(message):

    # Load private key from file
    key_path = f'{client_name}.pem'
    with open(key_path, 'rb') as f:
        private_key = RSA.import_key(f.read())

    # Sign a message using the private key
    hash = SHA256.new(message)
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(hash)

    return signature

def register(referenciaCliente, objetoServidor):
    
    # Generate private/public key pair
    key = RSA.generate(2048)

    # Save private key to a file
    private_key = key.export_key()
    key_path = f'{name}.pem'

    # Get public key
    public_key = key.publickey().export_key()

    """ 
    print("Digite sua chave pública:")
    password = input()

    print("Digite a URI do objeto remoto")
    uri = input()
    """

    message_bytes = public_key.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')


    res = auction_house.register(name, base64_message)
    if res==200:
        with open(key_path, 'wb') as f:
            f.write(private_key)
        print("Registration successful!")
        print("-------------------------------------")
        main_menu()
    elif res==500:
        print("Registration failed. Client already exists.")
        print("-------------------------------------")
        login()

def login(referenciaCliente, objetoServidor):
    res = auction_house.login(client_name)
    if res==200:
        print("Login successful!")
        print("-------------------------------------")
        thread = threading.Thread(target=callback.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        main_menu()

def create_auction():
    print("Digite o código do produto:")
    code = input()
    print("Digite o nome do produto:")
    name = input()
    print("Digite a descrição do produto:")
    description = input()
    print("Digite o preço inicial:")
    initial_price = float(input())
    print("Digite o tempo de término do leilão (em segundos):")
    end_time = int(input())
    if auction_house.create_auction(client_name, code, name, description, initial_price, end_time):
        print("####      leilão criado com sucesso!   ###")
        print("##########################################")
    else:
        print("####      leilão não criado.           ###")
        print("##########################################")

def bid_auction():
    print("Digite o código do item em leilão:")
    auction_code = input()
    print("Digite o valor do lance:")
    price = float(input())
    message = b'assinatura verificada'
    signature = get_signature(message)
    res = auction_house.bid_auction(auction_code, price, client_name, message, signature)
    if (res == 200):
        print("##       Bid placed successfully!       ##")
        print("##########################################")
    elif (res == 505):
        print("##    Bid failed. Invalid signature.    ##")
        print("##########################################")
    elif (res == 500):
        print("##  Bid failed. Current bid is higher.  ##")
        print("##########################################")
    elif (res == 503):
        print("##    Bid failed. Auction not found.    ##")
        print("##########################################")
    else:
        print("##      Bid failed. Server error.       ##")
        print("##########################################")

def show_auctions():
    auctions = auction_house.show_auctions()
    print("##########################################")
    print("########## leilões em andamento: #########")
    print("------------------------------------------")

    if auctions != None:
        for auction in auctions:
            print(auction)
        print("##########################################")           
    else:
        print("##     nenhum leilão em andamento.      ##")
        print("##########################################")           

def show_bids():
    bids = auction_house.get_bids(client_name)
    print("-------------------------------------")
    print(bids)

def exit():
    print("Saindo...")
    return 0

def main_menu():

    opc = 0

    def switch_case(opc):
        match opc:
            case 1:
                return show_auctions()
            case 2:
                return show_bids()
            case 3:
                return create_auction()
            case 4:
                return bid_auction()
            case 5:
                return exit()
            case _:
                print("Opção inválida")

    while opc != 5:
        print("##########################################")
        print("## bem-vindo à casa de leilões, " + client_name + "!")
        print("##        selecione uma opção:          ##")
        print("1: ver leilões em andamento")
        print("2: ver seus lances")
        print("3: criar um novo leilão")
        print("4: dar um lance em um leilão") 
        print("5: sair")
        print("##########################################")
        opc = int(input())
        switch_case(opc)

def main():

    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("auction.house")
    obj_servidor = Pyro5.api.Proxy(uri)
    print("Auction house is ready.")
    print("-------------------------------------")
    print("## bem-vindo à casa de leilões! por favor, insira seu nome:")
    print("## por favor, insira seu nome:")
    client_name = input()

    cliente = Client
    referenciaCliente = daemon.register(cliente)

    res = login(client_name, obj_servidor)

    if res == 500:
 
    elif res == 200:     
        print("Registro encontrado. Fazendo login...")
        main_menu()
    else:
        print("404 erro")
    
