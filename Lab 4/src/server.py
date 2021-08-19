import socket
import select
import threading
import json
import sys
import os 
from user import User

class Server:

    def __init__(self, host = '', port = 5000, pending_conn = 5, blocking = True):
        self.SERVER_IS_ALIVE     = True
        self.host                = host #'' possibilita acessar qualquer endereco alcancavel da maquina local 
        self.port                = port #Porta utilizada pelo processo para ouvir as mensagens
        self.blocking            = blocking
        self.inputs              = [sys.stdin]
        self.connections         = {} #Armazena histórico de conexões
        self.workers             = [] #Armazena as threads criadas.
        self.pending_conn        = pending_conn #Número de conexões que o servidor espera
        self.users               = {} #Armazena os usuários

        self.start()

    def start(self):
        self.sock                = socket.socket() #Cria um socket para a comunicação
        self.sock.bind((self.host, self.port)) #Vincula a interface e porta para comunicação
        self.sock.listen(self.pending_conn)  #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes
        self.sock.setblocking(self.blocking) #Configura o sock para o modo não-bloqueante
        self.inputs.append(self.sock) #Inclui o socket principal na lista de entradas de interesse
    
    def acceptConnection(self):
        newSock, ipAddress = self.sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou. OBS: A chamada pode ser bloqueante
        print ('Conectado com: ', ipAddress,'\n')

        return newSock, ipAddress
    
    def handleRequest(clientSock, ipAddress):

        while True:
            request_msg = clientSock.recv(1024) #Recebe a mensagem do processo ativo
            print(f'Mensagem recebida de {ipAddress}!')
            
            request = json.loads(request_msg) #Tranformar a mensagem recebida em um dicionário

            # Dicionário que guarda as chamadas dos métodos
            invokableMethods = {'logout'         : logoutClient(request['data']['userName']), 
                                'createAccount'  : createClientAccount(request['data']['userName'], request['data']['password']),
                                'deleteAccount'  : deleteClientAccount(request['data']['userName'], request['data']['password']),
                                'authAccount'    : authClientAccount(request['data']['userName'],   request['data']['password']),
                                'getMyStatus'    : getClientStatus(ipAddress),
                                'setMyStatus'    : setClientStatus(ipAddress, request['data']['status']),
                                'getUsers'       : getUsersList(),
                                'methodNotFound' : methodNotFound()
                                }

            response = invokableMethods.get(request['method'], invokableMethods['methodNotFound'])
           
            response_msg = json.dumps(response, ensure_ascii=False) #Gera o json para o envio da resposta ao cliente
            clientSock.send(bytes(response_msg,  encoding='utf-8')) #Envia mensagem de resposta para o processo ativo
            print(f'Mensagem devolvida para {ipAddress}!\n')

    def stop(self):
        self.saveData()

        self.sock.close()
        self.SERVER_IS_ALIVE = False
        print('Servidor finalizado!')

    def run(self):
        print('Iniciando o servidor...')
        print('Servidor está pronto para receber conexões.')

        while (self.SERVER_IS_ALIVE) :
            #espera por qualquer entrada de interesse
            read, write, exception = select.select(self.inputs, [], [])
            
            for trigger in read:
                if trigger == self.sock: #Caso o trigger seja um nova conexão
                    clientSock, ipAddress        = self.acceptConnection()
                    self.connections[clientSock] = ipAddress #Guarda a nova conexão
                    
                    worker                      = threading.Thread(target=handleRequest, args=(clientSock,ipAddress))
                    worker.start()
                    self.workers.append(worker)
                
                elif trigger == sys.stdin:
                    cmd = input().lower()
                    
                    if (cmd == 'fim'):
                        if(threading.active_count() - 1 != 0):
                            print('\nExistem conexões abertas com clientes.')
                            print('Novas conexões não serão aceitas.')
                            print('Aguardando a finalização dos clientes existentes...')

                            for c in self.workers: #Aguarda todos os processos terminarem
                                c.join()

                            print('Todos os clientes terminaram de usar o servidor.')

                        self.stop()
                        
                    elif (cmd == 'hist'):
                        print('\nHistórico de conexões:', list(self.connections.values()))
                        
                    elif (cmd == 'ativos'):
                        print(f'\nExistem {threading.active_count() - 1} clientes ativos.')
                    
                    else:
                        print("\nComando não existe.")


if __name__ == '__main__':
    
    server = Server(host = '', port = 5000, pending_conn = 10, blocking = False)
    server.run()
