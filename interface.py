import sys
import Pyro4
import Pyro4.util
from bidder import Bidder
from auction_house import AuctionHouse
from auction import Auction
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import cryptography

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

    print("Sua chave pública é:")
    print(pubkey.decode('utf-8'))
        
    print("Digite sua chave pública:")
    pubkey = input()
    print("Digite sua chave privada:")
    privkey = input() 
    print("Digite sua senha:")
    password = input()
    # criptografar senha com pubkey
    # encrypted_password = encrypt(password, pubkey)
    # salvar registro no servidor
    res = auction_house.register(name, pubkey, password)
    if (res == 200):
        # save private key in local storage
        with open("${name}.pem", "wb") as f:
            f.write(privkey.encode('utf-8'))
        print("Registration successful!")
        print("-------------------------------------")


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
        print("Auction created successfully!")
        print("-------------------------------------")
    else:
        print("Auction creation failed.")

def bid_auction():
    print("Digite o código do item em leilão:")
    auction_code = input()
    print("Digite o valor do lance:")
    price = float(input())
    res = auction_house.bid_auction(auction_code, price, client_name)
    if (res == 200):
        print("Bid placed successfully!")
        print("-------------------------------------")
    elif (res == 500):
        print("Bid failed. Not enough money.")
        print("-------------------------------------")
    elif (res == 400):
        print("Bid failed. Auction not found.")
        print("-------------------------------------")


def show_auctions():
    auctions = auction_house.show_auctions()
    print("-------- Available Auctions: --------")

    if auctions != None:
        for auction in auctions:
            print(auction)
    else:
        print("No auctions available.")
            
    print("-------------------------------------")

def show_bids():
    bids = auction_house.get_bids(client_name)
    print("-------------------------------------")
    print(bids)




sys.excepthook = Pyro4.util.excepthook

auction_house = Pyro4.Proxy("PYRONAME:auction.house")
print("Auction house is ready.")
print("-------------------------------------")
print("bem-vindo à casa de leilões! por favor, insira seu nome:")
client_name = input()
# if registro não encontrado, criar registro
# else retrieve objeto do cliente contendo pubkey
if auction_house.check_registration(client_name) == False:
    print("Registro não encontrado. Criando novo registro...")
    register(client_name)
else:     
    print("-------------------------------------")
    print("bem-vindo à casa de leilões, " + client_name + "!")

def exit():
    print("Saindo...")
    return 0


print("selecione uma opção:")
print("1: ver leilões em andamento")
print("2: ver seus lances")
print("3: criar um novo leilão")
print("4: dar um lance em um leilão") 
print("5: sair")
opc = int(input())

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

switch_case(opc)

while opc != 5:
    print("selecione uma opção:")
    print("1: ver leilões em andamento")
    print("2: ver seus lances")
    print("3: criar um novo leilão")
    print("4: dar um lance em um leilão") 
    print("5: sair")
    opc = int(input())
    switch_case(opc)
