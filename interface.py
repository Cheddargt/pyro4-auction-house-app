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

# cliente precisa ter: name, pyro_ref, bids
# TODO: não pode estar na interface.py
@Pyro5.api.expose
@Pyro5.api.callback
class Client(object):
    def __init__(self, name):
        self.name = name
        self.pyroRef = None
        self.bids = []

    def sendMessage(self, message):
        print(message)

    def loopThread(self, daemon):
        daemon.requestLoop()

    """ 
    File "/home/ghzeni/.local/lib/python3.10/site-packages/Pyro5/client.py", line 275, in _pyroInvoke
    raise data  # if you see this in your traceback, you should probably inspect the remote traceback as well
    AttributeError: remote object 'PYRO:obj_84cacf69426844a4ba0deb211b316cf1@localhost:42065' has no exposed attribute or method 'name' 
    """
    
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def setPyroRef(self, ref):
        self.pyroRef = ref

    def getPyroRef(self):
        return self.pyroRef
    
    def getBids(self):
        return self.bids
    
    def addBid(self, auctionName, auctionCode, price):

        # TODO: ajeitar ordem
        newBid = {
            "Nome": auctionCode,
            "Código": auctionName,
            "Lance": price,
        }

        self.bids.append(newBid)

    # pra printar o objeto
    def __str__(self):
        return f"Name: {self.name}\nBids: {self.bids}"

def getSignature(cliente):

    message = b'assinatura verificada'

    # Load private key from file
    key_path = f'{cliente.getName()}.pem'
    with open(key_path, 'rb') as f:
        private_key = RSA.import_key(f.read())

    # Sign a message using the private key
    hash = SHA256.new(message)
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(hash)

    # bytes -> b64 -> string
    sign_64 = base64.b64encode(signature)
    sign_string = sign_64.decode('utf-8')

    return sign_string

def createKeyPair(nomeCliente):

    # Generate private/public key pair
    key = RSA.generate(2048)

    # Save private key to a file
    private_key = key.export_key()
    key_path = f'{nomeCliente}.pem'
    with open(key_path, 'wb') as f:
        f.write(private_key)

    # Get public key
    public_key = key.publickey().export_key()

    # bytes -> b64 -> string
    key_64 = base64.b64encode(public_key)
    key_string = key_64.decode('utf-8')

    return key_string

def register(nomeCliente, objetoServidor):


    cliente = Client(nomeCliente)
    referenciaCliente = daemon.register(cliente)

    # """ 
    # print("Digite sua chave pública:")
    # password = input()

    # print("Digite a URI do objeto remoto")
    # uri = input()
    # """

    key64string = createKeyPair(nomeCliente)

    # nome do cliente, URI do objeto remoto do cliente e chave pública do cliente
    res = objetoServidor.register(nomeCliente, referenciaCliente, key64string)
    
    if res==200:
        # with open(key_path, 'wb') as f:
        #     f.write(private_key)
        print("## Registrado com sucesso!! ###############################")
        print("-----------------------------------------------------------")

        thread = threading.Thread(target=cliente.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        mainMenu(cliente, objetoServidor)
    elif res==500:
        print("## Registro falhou. Cliente já registrado. ################")
        print("###########################################################")
        login(cliente, objetoServidor)

def login(nomeCliente, objetoServidor):

    cliente = Client(nomeCliente)
    referenciaCliente = daemon.register(cliente)
    cliente.setPyroRef(referenciaCliente)
    # cliente.pyroRef = referenciaCliente

    res = objetoServidor.login(nomeCliente, referenciaCliente)

    if res==200:
        print("## Logado com sucesso! ####################################")
        print("## Bem-vindo à casa de leilões, " + cliente.name + "!!")
        print("###########################################################")

        thread = threading.Thread(target=cliente.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        mainMenu(cliente, objetoServidor)
    elif res==500:
        print("-----------------------------------------------------------")
        print("## Registro não encontrado. Criando novo registro... ######")
        register(nomeCliente, objetoServidor)
    else:
        print("404 erro")
        exit()

def createAuction(cliente, objetoServidor):
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
    if objetoServidor.createAuction(cliente.getName(), auction_code, name, description, initial_price, end_time):
        print("######----- Leilão criado com sucesso! ------##############")
        print("###########################################################")
    else:
        print("## Leilão não criado. #####################################")
        print("###########################################################")

def bidAuction(cliente, objetoServidor):

    print("Digite o código do item em leilão:")
    auction_code = input()
    print("Digite o valor do lance:")
    price = float(input())

    signature = getSignature(cliente)

    res = objetoServidor.bidAuction(cliente.getName(), auction_code, price, signature)

    if (res == 200):
        print("## Signature verified! ####################################")
        print("## Bid placed successfully!  ##############################")
        print("###########################################################")
    elif (res == 505):
        print("##    Bid failed. Invalid signature.    ##")
        print("###########################################################")
    elif (res == 500):
        print("##  Bid failed. Current bid is higher.  ##")
        print("##########################################")
    elif (res == 503):
        print("##    Bid failed. Auction not found.    ##")
        print("###########################################################")
    elif (res == 510):
        print("## Você não pode dar lance em um leilão criado por você. ##")
        print("###########################################################")
    else:
        print("##      Bid failed. Server error.       ##")
        print("###########################################################")

def showAuctions(objetoServidor):

    auctions = objetoServidor.showAuctions()
    print("###########################################################")
    print("## Leilões em andamento: ##################################")
    print("-----------------------------------------------------------")

    if auctions != None:
        for auction in auctions:
            print(auction)
        print("###########################################################")           
    else:
        print("## Nenhum leilão em andamento. ----------------------------")
        print("-----------------------------------------------------------")           

def showBids(cliente, objetoServidor):
    bids = objetoServidor.getBids(cliente.getName())

    if bids != None:
        print("###########################################################")
        print("## seus lances: ###########################################")
        print("-----------------------------------------------------------")
        print(bids)
    else:
        print("## Você ainda não deu nenhum lance. #######################")
        print("###########################################################") 

def exit():
    print("## Saindo...")
    return 0

def mainMenu(cliente, objetoServidor):

    opc = 0

    def switch_case(opc):
        match opc:
            case 1:
                return showAuctions(objetoServidor)
            case 2:
                return showBids(cliente, objetoServidor)
            case 3:
                return createAuction(cliente, objetoServidor)
            case 4:
                return bidAuction(cliente, objetoServidor)
            case 5:
                return exit()
            case _:
                print("Opção inválida")

    while opc != 5:
        print("###########################################################")
        print("## Selecione uma opção: ###################################")
        print("## 1: ver leilões em andamento ############################")
        print("## 2: ver seus lances #####################################")
        print("## 3: criar um novo leilão ################################")
        print("## 4: dar um lance em um leilão ###########################") 
        print("## 5: sair ################################################")
        print("###########################################################")
        opc = int(input())
        switch_case(opc)

def main():
    ns = Pyro5.api.locate_ns()
    uri = ns.lookup("auction.house")
    obj_servidor = Pyro5.api.Proxy(uri)
    print("Auction house is ready.")
    print("###########################################################")
    print("## bem-vindo à casa de leilões! por favor, insira seu nome:")
    print("## por favor, insira seu nome:")
    client_name = input()
    login(client_name, obj_servidor)
    print("###########################################################")


    
if __name__=="__main__":
    main()
