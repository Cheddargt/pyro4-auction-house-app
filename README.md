## How to Run

To run the auction house application, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install the required dependencies:
   ```
   pip install Pyro4
   ```

3. Open separate terminal windows or tabs for each of the following processes:

   **Terminal 1:**
   - Start the Pyro4 name server by running the following command:
     ```
     python -m Pyro4.naming
     ```

   **Terminal 2:**
   - Navigate to the project directory:
     ```
     cd pyro4-auction-house-app
     ```
   - Start the auction house server by running the following command:
     ```
     python auction_house.py
     ```

   **Terminal 3:**
   - Navigate to the project directory:
     ```
     cd auction-house-app
     ```
   - Start the interface for bidders by running the following command:
     ```
     python interface.py
     ```

4. Follow the prompts in the bidder interface to interact with the auction house. You can create bidders, view ongoing auctions, place bids, etc.

**Note:** Make sure the Pyro4 name server and the auction house server are running before starting the interface for bidders.

That's it! You can now run the auction house application and participate in auctions.

***
```PT-BR```

### Requisitos: 
- Execute um processo servidor e ao menos três processos clientes. Esses processos podem ser executados na mesma máquina. 
- Utilize PyRO (Python Remote Objects) para prover a comunicação entre os clientes e o servidor do leilão. 
- Cada cliente pode criar e participar de leilões. 
- Haverá apenas um serviço de nomes na máquina. O processo servidor criará esse serviço de nomes e registrará a aplicação Leilão nele. 

### Métodos disponíveis no servidor (valor 2,0): 
- Cadastro de usuário (valor 0,3): ao acessar o sistema pela primeira vez, cada cliente deve informar seu nome, sua chave pública e a URI do objeto remoto. Nesse cadastro, o cliente automaticamente atuará como subscriber, registrando interesse em receber notificações do servidor quando novos produtos para leilão forem cadastrados; 
- Consulta de leilões ativos (valor 0,2); 
- Cadastro de produto para leilão (código do produto, nome do produto, descrição do produto, preço inicial do produto e tempo final do leilão). Ao cadastrar um produto para leilão, o cliente atuará como subscriber, registrando interesse em receber notificações do servidor quando um novo lance for efetuado nesse produto ou quando o leilão desse produto for encerrado (valor 0,3) 
  + O leilão de um determinado produto deve ser finalizado quando o tempo definido para esse leilão expirar. Na finalização de um leilão, o servidor deve notificar esse evento a todos os clientes interessados neste leilão. Essa notificação deve conter as seguintes informações: a identificação do produto, nome completo do vencedor do produto, valor negociado (valor 0,3). 
- Lance em um produto. Os processos só podem efetuar lances crescentes (lance maior que o atual) para um determinado produto. Um processo pode efetuar quantos lances desejar. Ao tentar dar um lance em um produto de um leilão finalizado, o processo deverá receber uma mensagem de erro do servidor. Ao dar lance em um produto, o cliente atuará como subscriber, registrando interesse em receber notificações do servidor quando um novo lance for efetuado no produto de seu interesse ou quando o leilão desse produto for encerrado (valor 0,4); o Todo lance deve ser assinado digitalmente pelo cliente utilizando sua chave privada. Ao receber um lance, o servidor deverá checar a assinatura digital da mensagem utilizando a chave pública correspondente e somente aceitará o lance se a assinatura for válida (valor 0,5). 

### Método disponível no cliente (valor 0,5): 
- Notificação de evento: o processo servidor tem a tarefa de enviar, via chamada de método, notificações assíncronas de eventos, isto é, novos produtos para leilão (para todos os clientes cadastrados) e mudanças no andamento do leilão (novos lances em um produto e encerramento de leilão) aos clientes interessados (isto é, aos clientes que cadastraram o 
produto para leilão ou que efetuaram um lance no produto em questão). 

### Observações: 
- Desenvolva uma interface com recursos de interação apropriados. • É obrigatória a defesa da aplicação para obter a nota. 
- O desenvolvimento da aplicação pode ser individual ou em dupla.

***
```EN-US```

### Requirements
- Run one server process and at least three client processes. These processes can be executed on the same machine.
- Use PyRO (Python Remote Objects) to provide communication between the clients and the auction server.
- Each client can create and participate in auctions.
- There will be only one name service on the machine. The server process will create this name service and register the Auction application in it.

### Methods available on the server (score 2.0):
- User registration (score 0.3): When accessing the system for the first time, each client must provide their name, public key, and the URI of the remote object. In this registration, the client will automatically act as a subscriber, registering interest in receiving notifications from the server when new products are registered for auction.
- Active auctions query (score 0.2).
- Product registration for auction (product code, product name, product description, initial price, and auction end time). When registering a product for auction, the client will act as a subscriber, registering interest in receiving notifications from the server when a new bid is placed on this product or when the auction for this product is closed (score 0.3).
  + The auction for a particular product should be finished when the defined time for that auction expires. Upon the completion of an auction, the server should notify all interested clients of this event. This notification should contain the following information: product identification, full name of the winning bidder, and the negotiated value (score 0.3).
- Place a bid on a product. Processes can only place increasing bids (higher than the current bid) for a particular product. A process can place as many bids as desired. When attempting to place a bid on a product from a finished auction, the process should receive an error message from the server. When placing a bid on a product, the client will act as a subscriber, registering interest in receiving notifications from the server when a new bid is placed on the product of their interest or when the auction for that product is closed (score 0.4). All bids must be digitally signed by the client using their private key. Upon receiving a bid, the server should check the digital signature of the message using the corresponding public key and will only accept the bid if the signature is valid (score 0.5).

### Method available on the client (score 0.5):
- Event notification: The server process is responsible for sending asynchronous event notifications, i.e., new products for auction (to all registered clients) and changes in the auction progress (new bids on a product and auction closure) to interested clients (i.e., clients who registered the product for auction or placed a bid on the respective product).

### Notes:
- Develop an interface with appropriate interaction features.
- The defense of the application is mandatory to obtain a grade.
- The application can be developed individually or in pairs.

***
## Checklist

- [ ] Execute one server process and at least three client processes.
- [X] Use PyRO (Python Remote Objects) for communication between clients and the auction server.
- [ ] Allow each client to create and participate in auctions.
- [X] Set up only one name service on the machine and register the Auction application.
- [ ] Implement the following server methods:
  - [ ] User registration:
    - [ ] Prompt clients to provide name, public key, and URI of the remote object.
    - [ ] Automatically subscribe clients to receive notifications for new products registered for auction.
  - [ ] Active auctions query.
  - [ ] Product registration for auction:
    - [ ] Prompt clients to provide product code, name, description, initial price, and auction end time.
    - [ ] Automatically subscribe clients to receive notifications for new bids and auction closure for the registered product.
    - [ ] Finish the auction for a product when the defined time expires.
    - [ ] Notify all interested clients about the completion of an auction, including the product identification, winner's name, and negotiated value.
  - [ ] Place a bid on a product:
    - [ ] Only accept bids higher than the current bid for a particular product.
    - [ ] Notify clients who are subscribed to the product about new bids and auction closure.
    - [ ] Verify the digital signature of bids using the client's public key.
- [ ] Implement the following client method:
  - [ ] Event notification:
    - [ ] Receive asynchronous notifications from the server for new products and changes in auction progress (new bids and auction closure) for subscribed products.
- [ ] Develop an interface with appropriate interaction features.
- [ ] Prepare a defense of the application to obtain a grade.
- [ ] Optionally, allow the application to be developed individually or in pairs.


