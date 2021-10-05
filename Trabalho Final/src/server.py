import socket
import select
import threading
import json
import sys
import os 
from processLayer import ProcessLayer

class Server:
    
    def __init__(self, host = '', port = 5000, pending_conn = 50, blocking = True):
        self.SERVER_IS_ALIVE                = True             #Flag de controle
        self.host                           = host             #'' possibilita acessar qualquer endereco alcancavel da maquina local 
        self.port                           = port             #Porta utilizada pelo processo para ouvir as mensagens
        self.blocking                       = blocking         #Define se o socket será bloqueante ou não-bloqueante
        self.inputs                         = [sys.stdin]      #Lista que guarda o socket e o stdin
        self.connections                    = {}               #Armazena histórico de conexões
        self.usersSocket                    = {}               #Armazena uma relação userName-clientSocket
        self.workers                        = []               #Armazena as threads criadas.
        self.notifyThread                   = None             #Thread responsável pelo envio das mensagens para os clientes
        self.pending_conn                   = pending_conn     #Número de conexões que o servidor espera
        self.processLayer                   = ProcessLayer()   #Inicializa a classe responsável pela camada de processamento
        self.processLayer.readUsers()                          #Lê os dados do usuário
        self.processLayer.readChannels()                       #Lê os dados dos canais
        
        self.start()                                           #Inicia o servidor em relação ao seu socket

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

                if(response['status'] == 'success'):
                    self.usersSocket.pop(request['data']['userName'])
                    
            elif(request['method'] == 'createAccount'):
                response = self.processLayer.createClientAccount(request['data']['userName'], request['data']['password'])
            
            elif(request['method'] == 'deleteAccount'):
                response = self.processLayer.deleteClientAccount(request['data']['userName'], request['data']['password'])
            
            elif(request['method'] == 'authAccount'):
                response = self.processLayer.authClientAccount(request['data']['userName'], request['data']['password'])

                if(response['status'] == 'success'):
                    self.usersSocket[request['data']['userName']] = clientSock
            
            elif(request['method'] == 'createChannel'):
               response = self.processLayer.createChannel(request['data']['userName'], request['data']['password'], request['data']['channelName'])    

            elif(request['method'] == 'subscribeChannel'):
                response = self.processLayer.subscribeChannel(request['data']['userName'], request['data']['password'], request['data']['channelName'])
            
            elif(request['method'] == 'unsubscribeChannel'):
               response = self.processLayer.unsubscribeChannel(request['data']['userName'], request['data']['password'], request['data']['channelName'])

            elif(request['method'] == 'showMySubscriptions'):
                response = self.processLayer.showMySubscriptions(request['data']['userName'], request['data']['password'])
            
            elif(request['method'] == 'showMyOwnChannels'):
               response = self.processLayer.showMyOwnChannels(request['data']['userName'], request['data']['password'])
            
            elif(request['method'] == 'showAllChannels'):
                response = self.processLayer.showAllChannels()

            elif(request['method'] == 'publishChannel'):
               response = self.processLayer.publishChannel(request['data']['userName'], request['data']['password'], request['data']['channelName'], request['data']['message'] )
            
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
        self.processLayer.saveChannels()
        self.SERVER_IS_ALIVE = False
        self.notifyThread.join()
        self.sock.close()
        

        for item in self.connections:
            item.close()

        print('Servidor finalizado!')

        sys.exit(1)
         
    
    def notify(self):
        """
            Método responsável por identificar se ocorreu alguma publicação em algum canal e repassar a mensagem para os usuários que estão
            inscritos nos mesmos. 
        """ 
        while(self.SERVER_IS_ALIVE):

            channels = self.processLayer.findChannelWithMessage()
            
            for channel in channels:
                message = channel.getLastPublishedMessage()
                if (message is None):
                    continue

                for user in channel.getSubscribedUsers():
                    if(user in ProcessLayer.usersLogged):
                        clientSock = self.usersSocket[user]

                        message_to_send = {'method':'notifySubscriber', 'data': {'message': message, 'channelName': channel.getName()}}
                        response_msg = json.dumps(message_to_send, ensure_ascii=False) #Gera o json para o envio da resposta ao cliente
                        clientSock.send(bytes(response_msg,  encoding='utf-8')) #Envia mensagem de resposta para o cliente


    def run(self):
        """
            Método responsável por receber novas conexões e aceita comandos especiais do gerente do servidor
        """       
        print('Iniciando o servidor...')
        print('Servidor está pronto para receber conexões.')

        self.notifyThread = threading.Thread(target=self.notify)
        self.notifyThread.start()

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
                            print(f'\nExistem {threading.active_count() - 2} clientes ativos.')
                        
                        #Finaliza o servidor de modo abrupto/não elegante
                        elif (cmd == 'kill'):
                            self.stop()

                        else:
                            print("\nComando não existe.")
            except Exception as e:
                print(e)
                self.stop()

if __name__ == '__main__':
    # Estas duas linhas devem ser mantidas para que o servidor execute.
    server = Server(host = '', port = 5000, pending_conn = 100, blocking = False)
    server.run()
