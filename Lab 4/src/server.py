import socket
import select
import threading
import json
import sys
import os 
from processLayer import ProcessLayer

class Server:
    
    def __init__(self, host = '', port = 5000, pending_conn = 5, blocking = True):
        self.SERVER_IS_ALIVE     = True             #Flag de controle
        self.host                = host             #'' possibilita acessar qualquer endereco alcancavel da maquina local 
        self.port                = port             #Porta utilizada pelo processo para ouvir as mensagens
        self.blocking            = blocking         #Define se o socket será bloqueante ou não-bloqueante
        self.inputs              = [sys.stdin]
        self.connections         = {}               #Armazena histórico de conexões
        self.workers             = []               #Armazena as threads criadas.
        self.pending_conn        = pending_conn     #Número de conexões que o servidor espera
        self.processLayer        = ProcessLayer()   #Inicializa a classe responsável pela camada de processamento
        self.processLayer.readUsers()               #Lê os dados do usuário
        
        self.start()

    def start(self):
        """
            Cria o socket do servidor e o coloca a postos para aceitar conexões com os clientes.
        """         
        self.sock = socket.socket()             #Cria um socket para a comunicação
        self.sock.bind((self.host, self.port))  #Vincula a interface e porta para comunicação
        self.sock.listen(self.pending_conn)     #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes
        self.sock.setblocking(self.blocking)    #Configura o sock para o modo não-bloqueante
        self.inputs.append(self.sock)           #Inclui o socket principal na lista de entradas de interesse
    
    def acceptConnection(self):
        """
            Método por aceitar novas conexões com os clientes
            :return retorna o novo socket e a tupla (ip,port)
        """       
        newSock, ipAddress = self.sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou.
        print ('Conectado com: ', ipAddress,'\n')

        return newSock, ipAddress
    
    def handleRequest(self, clientSock, ipAddress):
        """
            Lida com a requisição feita pelo cliente, retornando o resultado do processamento do comando pedido por ele.
            :param clientSock: socket associado ao cliente em questão.
            :param ipAddress: endereço IP e porta do cliente em questão.
            :return mensagem de resposta resultado do processamento do comando.
        """        

        while True:
            request_msg = clientSock.recv(1024) #Recebe a mensagem do cliente
            print(f'Mensagem recebida de {ipAddress}!')
            
            if(request_msg == b''):
                break

            #Tranformar a mensagem recebida em um dicionário
            request = json.loads(request_msg) 

            if(request['method'] == 'logout'):
                response = self.processLayer.logoutClient(request['data']['userName'], request['data']['password'])
            elif(request['method'] == 'createAccount'):
                response = self.processLayer.createClientAccount(request['data']['userName'], request['data']['password'])
            elif(request['method'] == 'deleteAccount'):
                response = self.processLayer.deleteClientAccount(request['data']['userName'], request['data']['password'])
            elif(request['method'] == 'authAccount'):
                response = self.processLayer.authClientAccount(request['data']['userName'], request['data']['password'], (ipAddress[0], request['data']['port']))
            elif(request['method'] == 'getMyStatus'):
                response = self.processLayer.getClientStatus(request['data']['userName'], request['data']['password'])                
            elif(request['method'] == 'setMyStatus'):
                response = self.processLayer.setClientStatus(request['data']['userName'], request['data']['password'], request['data']['status'])
            elif(request['method'] == 'getUsers'):
                response = self.processLayer.getUsersList()
            else:
                response = self.processLayer.methodNotFound(request['method'])
           
            response_msg = json.dumps(response, ensure_ascii=False) #Gera o json para o envio da resposta ao cliente
            clientSock.send(bytes(response_msg,  encoding='utf-8')) #Envia mensagem de resposta para o cliente
            print(f'Mensagem devolvida para {ipAddress}!\n')

    def stop(self):
        """
            Método responsável por matar o servidor
        """       
        self.processLayer.saveUsers()

        self.sock.close()
        self.SERVER_IS_ALIVE = False

        for item in self.connections:
            item.close()

        print('Servidor finalizado!')

        sys.exit(1)
        
    def run(self):
        """
            Método responsável por receber novas conexões e aceita comandos especiais do gerente do servidor
        """       
        print('Iniciando o servidor...')
        print('Servidor está pronto para receber conexões.')

        while (self.SERVER_IS_ALIVE) :

            try:
                #Espera por qualquer entrada de interesse
                read, write, exception = select.select(self.inputs, [], [])
                
                for trigger in read:
                    if trigger == self.sock: #Caso o trigger seja um nova conexão
                        clientSock, ipAddress        = self.acceptConnection()
                        self.connections[clientSock] = ipAddress #Guarda a nova conexão
                        
                        worker                      = threading.Thread(target=self.handleRequest, args=(clientSock,ipAddress))
                        worker.start()
                        self.workers.append(worker)
                    
                    elif trigger == sys.stdin:
                        cmd = input().lower()
                        
                        #Finaliza o servidor elegantemente
                        if (cmd == 'fim'):
                            if(threading.active_count() - 1 != 0):
                                print('\nExistem conexões abertas com clientes.')
                                print('Novas conexões não serão aceitas.')
                                print('Aguardando a finalização dos clientes existentes...')

                                for c in self.workers: #Aguarda todos os processos terminarem
                                    c.join()

                                print('Todos os clientes terminaram de usar o servidor.')

                            self.stop()
                        
                        #Mostra histórico de conexões
                        elif (cmd == 'hist'):
                            print('\nHistórico de conexões:', list(self.connections.values()))
                        
                        #Mostra o número de threads clientes ativas
                        elif (cmd == 'ativos'):
                            print(f'\nExistem {threading.active_count() - 1} clientes ativos.')
                        
                        #Finaliza o servidor de modo abrupto/não elegante
                        elif (cmd == 'kill'):
                            for key,value in self.processLayer.users.items():
                                self.processLayer.users[key].setStatus(-1)
                                self.processLayer.users[key].setIP('')
                                self.processLayer.users[key].setPort(0)
                            self.stop()

                        else:
                            print("\nComando não existe.")
            except Exception as e:
                print(e)
                self.stop()

if __name__ == '__main__':
    server = Server(host = '', port = 5000, pending_conn = 10, blocking = False)
    server.run()
