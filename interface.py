import sys
import Pyro4
import Pyro4.util
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import cryptography
from client import Client
global client_name
global uri
global pubkey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import threading

daemon = Pyro4.Daemon()

def encrypt_message(msg):
    private_key_path = f'{client_name}.pem'
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            backend=default_backend()
        )

    # message = bytes(msg, encoding='utf-8')
    message = b"Verified"
    encrypted_message = private_key.sign(
        message,
        padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )   

    return encrypted_message

def register(name):
    # Generate a new RSA key pair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Get the public key from the private key
    public_key = private_key.public_key()

    # Serialize the public key to PEM format
    pubkey = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Serialize the private key to PEM format
    private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
    )

    """ 
    print("Digite sua chave pública:")
    password = input()

    print("Digite a URI do objeto remoto")
    uri = input()
    """

    uri = "PYRONAME:auction.house"

    client = Client(client_name, pubkey)

    uri = daemon.register(client)
    nameserver = Pyro4.locateNS()
    nameserver.register(f'{client_name}', uri)

    req_loop = threading.Thread(target=lambda : daemon.requestLoop())
    req_loop.start()

    res = auction_house.register(name, pubkey)
    if res==200:
        private_key_path = f'{name}.pem'
        with open(private_key_path, "wb") as file:
            file.write(private_key_pem)
        print("Registration successful!")
        print("-------------------------------------")
        main_menu()
    elif res==500:
        print("Registration failed. Client already exists.")
        print("-------------------------------------")
        login()

def login():
    res = auction_house.login(client_name)
    if res==200:
        print("Login successful!")
        print("-------------------------------------")
        req_loop = threading.Thread(target=lambda : daemon.requestLoop())
        req_loop.start()
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
    # enc_msg = encrypt_message('signature_verified')
    enc_msg = 'signature_verified'
    res = auction_house.bid_auction(auction_code, price, client_name, enc_msg)
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

sys.excepthook = Pyro4.util.excepthook
auction_house = Pyro4.Proxy("PYRONAME:auction.house")
print("Auction house is ready.")
print("-------------------------------------")
print("## bem-vindo à casa de leilões! por favor, insira seu nome:")
print("## por favor, insira seu nome:")
client_name = input()

if auction_house.check_registration(client_name) == False:
    print("Registro não encontrado. Criando novo registro...")
    register(client_name)
else:     
    print("Registro encontrado. Fazendo login...")
    main_menu()
    
