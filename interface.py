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
class ClientCallback(object):
    def __init__(self, name):
        self.name = name
        self.pyroRef = None
        self.bids = []

    # usados pela professora
    #####################################
    def sendMessage(self, message):
        print(message)

    def loopThread(self, daemon):
        daemon.requestLoop()
    #####################################

def getSignature(nomeCliente):

    message = b'assinatura verificada'

    # Load private key from file
    key_path = f'{nomeCliente}.pem'
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

    # TODO: tirar daqui
    clienteCallback = ClientCallback(nomeCliente)
    referenciaCliente = daemon.register(clienteCallback)

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

        thread = threading.Thread(target=clienteCallback.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        mainMenu(nomeCliente, clienteCallback, objetoServidor)
    elif res==500:
        print("## Registro falhou. Cliente já registrado. ################")
        print("###########################################################")
        login(nomeCliente, clienteCallback, objetoServidor)

def login(nomeCliente, objetoServidor):

    clienteCallback = ClientCallback(nomeCliente)
    referenciaCliente = daemon.register(clienteCallback)

    res = objetoServidor.login(nomeCliente, referenciaCliente)

    if res==200:
        print("## Logado com sucesso! ####################################")
        print("## Bem-vindo à casa de leilões, " + nomeCliente + "!!")
        print("###########################################################")

        thread = threading.Thread(target=clienteCallback.loopThread, args=(daemon, ))
        thread.daemon = True
        thread.start()
        mainMenu(nomeCliente, clienteCallback, objetoServidor)
    elif res==500:
        print("-----------------------------------------------------------")
        print("## Registro não encontrado. Criando novo registro... ######")
        register(nomeCliente, objetoServidor)
    else:
        print("404 erro")
        exit()

def createAuction(nomeCliente, clienteCallback, objetoServidor):
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
    if objetoServidor.createAuction(nomeCliente, auction_code, name, description, initial_price, end_time):
        print("######----- Leilão criado com sucesso! ------##############")
        print("###########################################################")
    else:
        print("## Leilão não criado. #####################################")
        print("###########################################################")

def bidAuction(nomeCliente, clienteCallback, objetoServidor):

    print("Digite o código do item em leilão:")
    auction_code = input()
    print("Digite o valor do lance:")
    price = float(input())

    signature = getSignature(nomeCliente)

    res = objetoServidor.bidAuction(nomeCliente, auction_code, price, signature)

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

def showBids(nomeCliente, clienteCallback, objetoServidor):
    bids = objetoServidor.getBids(nomeCliente)

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

def mainMenu(nomeCliente, clienteCallback, objetoServidor):

    opc = 0

    def switch_case(opc):
        match opc:
            case 1:
                return showAuctions(objetoServidor)
            case 2:
                return showBids(nomeCliente, clienteCallback, objetoServidor)
            case 3:
                return createAuction(nomeCliente, clienteCallback, objetoServidor)
            case 4:
                return bidAuction(nomeCliente, clienteCallback, objetoServidor)
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
