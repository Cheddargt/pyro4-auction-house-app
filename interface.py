import sys
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

sys.excepthook = Pyro5.errors.excepthook


class Client(object):
    def __init__(self, name):
        self.name = name
        self.pyroRef = ''
        self.bids = {}

    @Pyro5.api.expose
    @Pyro5.api.callback
    def send_message(self, message):
        print(message)

    def loopThread(daemon):
        daemon.requestLoop()
    
    def setPyroRef(self, ref):
        self.pyroRef = ref

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

def register(nomeCliente, objetoServidor):


    cliente = Client(nomeCliente)
    referenciaCliente = daemon.register(cliente)
    
    # Generate private/public key pair
    key = RSA.generate(2048)

    # Save private key to a file
    private_key = key.export_key()
    key_path = f'{nomeCliente}.pem'

    # Get public key
    public_key = key.publickey().export_key()

    """ 
    print("Digite sua chave pública:")
    password = input()

    print("Digite a URI do objeto remoto")
    uri = input()
    """

    # bytes -> b64 -> string
    key_64 = base64.b64encode(public_key)
    key_string = key_64.decode('utf-8')

    # seu nome, sua chave pública e a URI do objeto remoto (do cliente)
    res = objetoServidor.register(nomeCliente, key_string, referenciaCliente)
    
    if res==200:
        with open(key_path, 'wb') as f:
            f.write(private_key)
        print("Registration successful!")
        print("-------------------------------------")
        thread = threading.Thread(target=cliente.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        main_menu()
    elif res==500:
        print("Registration failed. Client already exists.")
        print("-------------------------------------")
        login()

def login(nomeCliente, objetoServidor):

    cliente = Client(nomeCliente)
    referenciaCliente = daemon.register(cliente)
    cliente.setPyroRef(referenciaCliente)
    # cliente.pyroRef = referenciaCliente

    res = objetoServidor.login(nomeCliente, referenciaCliente)

    if res==200:
        print("Login successful!")
        print("-------------------------------------")
        thread = threading.Thread(target=cliente.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        main_menu(cliente, objetoServidor)
    elif res==500:
        print("Registro não encontrado. Criando novo registro...")
        register(nomeCliente, objetoServidor)
    else:
        print("404 erro")
        exit()

def create_auction(cliente, objetoServidor):
    print("Digite o código do produto:")
    auction_code = input()
    print("Digite o nome do produto:")
    name = input()
    print("Digite a descrição do produto:")
    description = input()
    print("Digite o preço inicial:")
    initial_price = float(input())
    print("Digite o tempo de término do leilão (em segundos):")
    end_time = int(input())
    if objetoServidor.create_auction(cliente.pyroRef, auction_code, name, description, initial_price, end_time):
        print("####      leilão criado com sucesso!   ###")
        print("##########################################")
    else:
        print("####      leilão não criado.           ###")
        print("##########################################")

def bid_auction(cliente, objetoServidor):
    print("Digite o código do item em leilão:")
    auction_code = input()
    print("Digite o valor do lance:")
    price = float(input())
    message = b'assinatura verificada'
    signature = get_signature(message)
    # Todo lance deve ser assinado digitalmente pelo cliente utilizando sua chave privada.
    res = objetoServidor.bid_auction(cliente.pyroRef, auction_code, price, message, signature)
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

def show_auctions(objetoServidor):

    auctions = objetoServidor.show_auctions()
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

def show_bids(cliente, objetoServidor):
    bids = objetoServidor.get_bids(cliente.pyroRef)
    print("-------------------------------------")
    print(bids)

def exit():
    print("Saindo...")
    return 0

def main_menu(cliente, objetoServidor):

    opc = 0

    def switch_case(opc):
        match opc:
            case 1:
                return show_auctions(objetoServidor)
            case 2:
                return show_bids(cliente, objetoServidor)
            case 3:
                return create_auction(cliente, objetoServidor)
            case 4:
                return bid_auction(cliente, objetoServidor)
            case 5:
                return exit()
            case _:
                print("Opção inválida")

    while opc != 5:
        print("##########################################")
        print("## bem-vindo à casa de leilões, " + cliente.name + "!")
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
    login(client_name, obj_servidor)
    
if __name__=="__main__":
    main()
