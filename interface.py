import sys
import Pyro4
import Pyro4.util
from bidder import Bidder
from auction_house import AuctionHouse
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
    """     
    print("Digite sua chave pública:")
    pubkey = input()
    print("Digite sua chave privada:")
    privkey = input() 
    """
    print("Digite sua senha:")
    password = input()
    # criptografar senha com pubkey
    # encrypted_password = encrypt(password, pubkey)
    # salvar registro no servidor
    auction_house.register(name, pubkey, password)

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
    auction_house.create_auction(client_name, code, name, description, initial_price, end_time)

def bid_auction():
    print("Digite o nome do leilão:")
    auction_name = input()
    print("Digite o valor do lance:")
    price = float(input())
    auction_house.bid_auction(auction_name, price, client_name)


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
            return auction_house.show_auctions()
        case 2:
            return auction_house.show_bids()
        case 3:
            return create_auction()
        case 4:
            return auction_house.bid_auction()
        case 5:
            return auction_house.exit()
        case _:
            print("Opção inválida")

switch_case(opc)