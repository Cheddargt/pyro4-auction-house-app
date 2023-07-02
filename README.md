## TODO
- [ ] Fix 'ver seus lances' not showing user bids
- [ ] Fix notification service
- [ ] Fix signature service


## How to Run

To run the auction house application, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Install the required dependencies:
   ```
   pip install Pyro5
   ```

3. Open separate terminal windows or tabs for each of the following processes:

   **Terminal 1:**
   - Start the Pyro5 name server by running the following command:
     ```
     python -m Pyro5.nameserver
     ```

   **Terminal 2:**
   - Start the auction house server by running the following command:
     ```
     python auction_house.py
     ```

   **Terminal 3:**
   - Start the interface for bidders by running the following command:
     ```
     python interface.py
     ```

4. Follow the prompts in the bidder interface to interact with the auction house. You can create bidders, view ongoing auctions, place bids, etc.

**Note:** Make sure the Pyro5 name server and the auction house server are running before starting the interface for bidders.

That's it! You can now run the auction house application and participate in auctions.

***
```PT-BR```

### Requisitos: 
- [x] Execute um processo servidor e ao menos três processos clientes. Esses processos podem ser executados na mesma máquina. 
- [x] Utilize PyRO (Python Remote Objects) para prover a comunicação entre os clientes e o servidor do leilão. 
- [x] Cada cliente pode criar e participar de leilões. 
- [x] Haverá apenas um serviço de nomes na máquina. O processo servidor criará esse serviço de nomes e registrará a aplicação Leilão nele. 

### Métodos disponíveis no servidor (valor 2,0): 
- [x] Cadastro de usuário (valor 0,3): ao acessar o sistema pela primeira vez, cada cliente deve informar seu nome, sua chave pública e a URI do objeto remoto. Nesse cadastro, o cliente automaticamente atuará como subscriber, registrando interesse em receber notificações do servidor quando novos produtos para leilão forem cadastrados; 
- [x] Consulta de leilões ativos (valor 0,2); 
- [x] Cadastro de produto para leilão (código do produto, nome do produto, descrição do produto, preço inicial do produto e tempo final do leilão). Ao cadastrar um produto para leilão, o cliente atuará como subscriber, registrando interesse em receber notificações do servidor quando um novo lance for efetuado nesse produto ou quando o leilão desse produto for encerrado (valor 0,3) 
  - [x]  O leilão de um determinado produto deve ser finalizado quando o tempo definido para esse leilão expirar. Na finalização de um leilão, o servidor deve notificar esse evento a todos os clientes interessados neste leilão. Essa notificação deve conter as seguintes informações: a identificação do produto, nome completo do vencedor do produto, valor negociado (valor 0,3). 
- [x]  Lance em um produto. Os processos só podem efetuar lances crescentes (lance maior que o atual) para um determinado produto. Um processo pode efetuar quantos lances desejar. Ao tentar dar um lance em um produto de um leilão finalizado, o processo deverá receber uma mensagem de erro do servidor. Ao dar lance em um produto, o cliente atuará como subscriber, registrando interesse em receber notificações do servidor quando um novo lance for efetuado no produto de seu interesse ou quando o leilão desse produto for encerrado (valor 0,4); 
- [ ]  Todo lance deve ser assinado digitalmente pelo cliente utilizando sua chave privada. Ao receber um lance, o servidor deverá checar a assinatura digital da mensagem utilizando a chave pública correspondente e somente aceitará o lance se a assinatura for válida (valor 0,5). 

### Método disponível no cliente (valor 0,5): 
- [x]  Notificação de evento: o processo servidor tem a tarefa de enviar, via chamada de método, notificações assíncronas de eventos, isto é, novos produtos para leilão (para todos os clientes cadastrados) e mudanças no andamento do leilão (novos lances em um produto e encerramento de leilão) aos clientes interessados (isto é, aos clientes que cadastraram o produto para leilão ou que efetuaram um lance no produto em questão). 

### Observações: 
- [x]  Desenvolva uma interface com recursos de interação apropriados. • É obrigatória a defesa da aplicação para obter a nota. 
- [x]  O desenvolvimento da aplicação pode ser individual ou em dupla.

***
## Checklist

- [x] Execute one server process and at least three client processes.
- [X] Use PyRO (Python Remote Objects) for communication between clients and the auction server.
- [x] Allow each client to create and participate in auctions.
- [X] Set up only one name service on the machine and register the Auction application.
- [x] Implement the following server methods:
  - [x] User registration:
    - [x] Prompt clients to provide name, public key, and URI of the remote object.
    - [x] Automatically subscribe clients to receive notifications for new products registered for auction.
  - [x] Active auctions query.
  - [x] Product registration for auction:
    - [x] Prompt clients to provide product code, name, description, initial price, and auction end time.
    - [x] Automatically subscribe clients to receive notifications for new bids and auction closure for the registered product.
    - [x] Finish the auction for a product when the defined time expires.
    - [x] Notify all interested clients about the completion of an auction, including the product identification, winner's name, and negotiated value.
  - [x] Place a bid on a product:
    - [x] Only accept bids higher than the current bid for a particular product.
    - [x] Notify clients who are subscribed to the product about new bids and auction closure.
    - [ ] Verify the digital signature of bids using the client's public key.
- [x] Implement the following client method:
  - [x] Event notification:
    - [x] Receive asynchronous notifications from the server for new products and changes in auction progress (new bids and auction closure) for subscribed products.
- [x] Develop an interface with appropriate interaction features.
- [x] Prepare a defense of the application to obtain a grade.
- [x] Optionally, allow the application to be developed individually or in pairs.


