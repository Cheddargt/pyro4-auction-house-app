import Pyro4

class Client(object):
    def __init__(self, name):
        self.name = name
        self.bids = {}

    # acessível remotamente
    @Pyro4.expose
    def send_message(self, message):
        print(message)

    # pra printar o objeto
    def __str__(self):
        return f"Name: {self.name}\nBids: {self.bids}"