import socket
import select
import threading
import json
import sys
import traceback
import os
import random
from clientInterface import ClientInterface
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS, OPEN_CHAT, CLOSE_CHAT, DELETE_MESSAGES, SEND_MESSAGE

class Client:

    def __init__(self, serverHost='localhost', serverPort = 5000):
        self.serverHost         = serverHost        #Endereço do processo passivo
        self.serverPort         = serverPort        #Porta que o processo passivo estará escutando
        self.myPort             = None              #Porta que o cliente irá receber as conexões de outros clientes
        self.sock               = None              #Sock utilizado para se comunicar com o servidor
        self.clientView         = ClientInterface() #Inicializa a classe responsável pela interface da aplicação
        self.userName           = ''                #Guarda o user name do usuário
        self.password           = ''                #Guarda a senha do usuário
        self.status             = -1                #Guarda o status do usuário
        self.stopWorkers        = False             #Variável chave para parar todas as threads trabalhadoras
        self.chatUsersIps       = {}                #Ips dos usuários cadastrados no sistema
        self.chatUsersPorts     = {}                #Portas dos usuários cadastrados no sistema
        self.chatUsersStatus    = {}                #Status dos usuários cadastrados no sistema
        self.openChat           = {}                #Usuários com os quais se mantém a conversa ativa
        self.openChatMessages   = {}                #Guarda as conversas com os demais usuários. Ex:{'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.fifoMessages       = {}                #Fila de envio de mensagens trocadas entre usuários. Ex:{'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.lock               = threading.Lock()  #Inicializa o lock
        self.start()                                #Adquire o socket e se conecta com o servidor

    def scanPort(self):
        """
            Encontra uma porta vaga para o cliente.
            :return Porta não ocupada no cliente.
        """

        ip = socket.gethostbyname(socket.gethostname())

        # Define uma porta que esteja disponível
        for port in range(random.randrange(2000,4000),65535):
            try:
                serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                serv.bind((ip,port))
            except:
                print('[OPEN] Port open :',port)
                serv.close()
                continue

            serv.close()
            return port
                
    def start(self):
        """
            Cria o socket do cliente e o conecta com o servidor.
        """        
        self.sock = socket.socket()
        try:
            self.sock.connect((self.serverHost, self.serverPort)) #Abertura da conexão com o servidor
        except Exception as e:
            sys.exit(1)

    def stop(self):
        """
            Fecha o socket do cliente.
        """        
        self.sock.close()

    def finishBusiness(self):
        """
            Termina as threads trabalhadoras e o fluxo passivo (P2P) do cliente.
        """        
        self.stopWorkers = True
        sock = socket.socket()
        sock.connect(('localhost', self.myPort))
        sock.close()
        
    def handlerServerRequest(self, method, userInput):
        """
            Dado o método e o input do cliente, gera a mensagem de requisição para o servidor e envia para o mesmo.
            :param method: comando a ser executado.
            :param userInput: entradas digitadas pelo cliente.
            :return mensagem de resposta do servidor.
        """
        methods = {CREATE_ACCOUNT: 'createAccount', DELETE_ACCOUNT: 'deleteAccount', LOGIN:'authAccount', ACTIVE_USERS:'getUsers', LOGOUT:'logout', EXIT:'logout', ACTIVE_STATUS:'setMyStatus', INACTIVE_STATUS:'setMyStatus'}

        if(method in (CREATE_ACCOUNT, DELETE_ACCOUNT)):
            userName, password = userInput
            request            = {'method':methods[method],'data':{'userName': userName,'password':password}}

        if(method == LOGIN):
            self.myPort = self.scanPort()
            userName, password = userInput
            request            = {'method':methods[method],'data':{'userName': userName, 'password':password, 'port':self.myPort}}

        elif(method == ACTIVE_USERS):
            request = {'method':methods[method],'data': None}

        elif(method == ACTIVE_STATUS):
            request = {'method':methods[method],'data':{'userName': self.userName,'password': self.password,'status':1}}
        
        elif(method == INACTIVE_STATUS):
            request = {'method':methods[method],'data':{'userName': self.userName,'password': self.password,'status':0}}
        
        elif(method in (LOGOUT, EXIT)):
            request = {'method':methods[method],'data':{'userName': self.userName,'password': self.password}}

        request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
        self.sock.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o servidor
        
        response_msg = self.sock.recv(1024) #Recebimento da mensagem enviada pelo servidor.
        response     = json.loads(response_msg) #Tranformar a mensagem recebida em um dicionário.

        return response

    def handleServerResponse(self, method, response, userInput):
        """
            Dado a resposta do servidor e o input do cliente faz as tratativas necessárias no back do cliente.
            :param method: comando a ser executado
            :param response: resposta retornada pelo servidor
            :param userInput: possíveis entradas digitadas pelo usuário
            :return void ou mensagem de retorno para a interface.
        """
        #Atualiza as informação do usuário e iniciar o lado passivo do cliente para receber futuras conexões P2P
        if(method == LOGIN and response['status'] == 'success'):
            userName, password          = userInput
            self.userName               = userName
            self.clientView.username    = self.userName
            self.password               = password
            self.status                 = 1

            work = threading.Thread(target= self.runAsPassive_P2P, args=())
            work.start()

        if(method == ACTIVE_STATUS and response['status'] == 'success'):
            self.status = 1
        
        if(method == INACTIVE_STATUS and response['status'] == 'success'):
            self.status = 0

        #Quando um usuário se desloga, é necessário trocar seu status para offline e terminar suas threads trabalhadoras associadas assim como o fluxo passivo
        if(method == LOGOUT and response['status'] == 'success'): 
            self.status = -1
            self.finishBusiness()

        #Ao abrir um chat, as informações dos demais usuários são atualizados a partir das informações do servidor
        if(method == OPEN_CHAT and response['status'] == 'success'): 
            self.lock.acquire()
            for element in response['data']:
                self.chatUsersIps[element['userName']]       = element['ip']
                self.chatUsersPorts[element['userName']]     = element['port']
                self.chatUsersStatus[element['userName']]    = element['status']
            self.lock.release()

            response = {'method':'openChat', 'status': 'success', 'data':{'message': None} }
            return response
        
        elif(method == OPEN_CHAT and response['status'] == 'error'):
            response = {'method':'openChat', 'status': 'error', 'data':{'message': None} }
            return response

    def handleInterfaceCommand(self, cmd, userInput = None, response = None):
        """
            Dado o comando enviado e outras possíveis informações (entrada do usuário ou resposta a requisição), trata os comandos da interface.
            :param cmd: comando a ser executado.
            :param userInput: entradas digitadas pelo cliente.
            :param response: mensagem de resposta (dicionário).
            :return void ou mensagem de resposta (dicionário) para a classe clientInterface.
        """
    
        if(cmd == OPEN_CHAT):
            
            #Caso o usuário com quem se deseja falar não esteja ativo, retorna uma mensagem de erro para a interface 
            if(userInput[5:] not in self.chatUsersStatus):
                response = {'method':'openChat', 'status': 'error', 'data':{'message': None} }
            
            #Caso eu já tenha uma conversa ativa com o usuário em questão, apenas retorna uma mensagem de sucesso para interface, sem mudanças no back.
            elif(userInput[:5] == OPEN_CHAT and self.status == 1 and (userInput[5:] in self.openChat and self.openChat[userInput[5:]] == 1) 
            and self.chatUsersStatus[userInput[5:]] == '1'):
                
                response = {'method':'openChat', 'status': 'success', 'data':{'message': None} }
                self.clientView.openChatFriendUser = userInput[5:]
            
            #Caso ainda não exista uma conversa ativa com o usuário em questão, será iniciada uma conversa com o mesmo ao iniciar o lado ativo P2P 
            else:
                response = self.handlerServerRequest(ACTIVE_USERS, None)
                response = self.handleServerResponse(OPEN_CHAT,response,None)
                if(response['status'] == 'success'):
                    response = self.runAsActive_P2P(userInput)
                    if(response['status'] == 'success'):
                        self.clientView.openChatFriendUser = userInput[5:]

        elif(cmd == CLOSE_CHAT):
            self.clientView.openChatFriendUser = None
            response = {'method':'closeChat', 'status': 'success', 'data':{'message': None} }

        #Ao se logar, deve-se atualizar as informações dos usuários cadastrados na aplicação 
        elif(cmd == LOGIN and (response['status'] == 'success')):
            self.stopWorkers    = False
            responseUpdate      = self.handlerServerRequest(ACTIVE_USERS, None)
            self.handleServerResponse(OPEN_CHAT,responseUpdate,None)
            
            response = None

        elif(cmd == DELETE_MESSAGES):
            self.openChatMessages[self.clientView.openChatFriendUser] = []
            response = {'method':'deleteMessages', 'status': 'success', 'data':{'message': None} }
        
        #As mensagens a serem enviadas devem ser adicionadas a fila de mensagens     
        elif(cmd == SEND_MESSAGE):
            
            self.lock.acquire()
            self.openChatMessages[self.clientView.openChatFriendUser].append(self.userName + ":" + userInput)
            if(self.clientView.openChatFriendUser not in self.fifoMessages):
                    self.fifoMessages[self.clientView.openChatFriendUser] = []
            self.fifoMessages[self.clientView.openChatFriendUser].append(userInput)
            self.lock.release()

            response = None
            
        return response

    def channelMessage(self, chatUserName, clientSock):
        """
            Perfoma como um canal de mensagens para a comunicação cliente-cliente. Aqui é onde o cliente (independente se está como passivo ou ativo no P2P) envia e recebe mensagens de outros clientes.
            :param chatUserName: user name do usuário que o cliente em questão está conversando.
            :param clientSock: socket do cliente em questão.
        """        
        request_msg = None

        if(chatUserName not in self.openChatMessages):
            self.openChatMessages[chatUserName] = []
        try:
            while True:

                try:
                    #Recebe a mensagem do par de conversa
                    request_msg = clientSock.recv(1024) 
                except socket.timeout as e:
                    pass
                
                #Entra se receber logout ou se deseja terminar as threads
                if(request_msg == b'' or self.stopWorkers): 
                    self.lock.acquire()
                    self.openChat[chatUserName] = 0
                    self.lock.release()
                    clientSock.close()
                    break

                if(request_msg != None):
                    #Separa as mensagens recebidas caso venha várias de uma vez só
                    request_msg = str(request_msg, encoding='utf-8').replace('}{','}-#-{').split('-#-')
                    for r in request_msg:
                        request = json.loads(r)                
                        if(request['method'] == 'logout'):
                            self.lock.acquire()
                            self.openChat[chatUserName] = 0
                            self.lock.release()
                            clientSock.close()
                            break

                        self.lock.acquire()
                        #Salva a mensagem recebida na lista de mensagens com aquele par de conversa
                        self.openChatMessages[chatUserName].append(chatUserName + ":" + request['data']['message'])
                        self.lock.release()
                
                #É responsável por enviar todas as mensagens que estão na fila de mensagem a serem enviadas.
                self.lock.acquire()
                for i in range(len(self.fifoMessages.get(chatUserName,[]))):
                    msg = self.fifoMessages[chatUserName][0] 
                    request = {'method': 'sendMessage', 'data':{'userName': self.userName, 'message': msg}}
                    request_msg = json.dumps(request, ensure_ascii=False) 
                    clientSock.send(bytes(request_msg,  encoding='utf-8')) 
                    self.fifoMessages[chatUserName].pop(0)

                self.clientView.messages_queue = self.openChatMessages
                if(self.clientView.openChatFriendUser == chatUserName):
                    self.clientView.printChatScreen()
                self.lock.release()

                request_msg = None
                
        except Exception as e:
            self.lock.acquire()
            self.openChat[chatUserName] = 0
            self.lock.release()
            clientSock.close()
    
    def runAsActive_P2P(self, userInput):
        """
            Representa o fluxo ativo da implementação P2P, para quando o cliente deseja tomar a iniciativa de iniciar a conversa com outro.
            :param userInput: comando de chat digitado pelo usuário em questão para iniciar uma conversa com outro. Ex: "chat:nick"
        """         
        if(userInput[:5] == OPEN_CHAT and self.status == 1 and self.chatUsersStatus[userInput[5:]] == '1'
        and ((not userInput[5:] in self.openChat)  or (userInput[5:] in self.openChat and self.openChat[userInput[5:]] == 0))):
            try:

                sock_active = socket.socket()
                #Abertura da conexão com o processo passivo do cliente que se deseja comunicar
                sock_active.connect((self.chatUsersIps[userInput[5:]], self.chatUsersPorts[userInput[5:]]))
                sock_active.setblocking(True) #Configura o sock para o modo bloqueante

                request     = {'method': 'sendMessage', 'data':{'userName': self.userName, 'message': 'hand shake'}}
                request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao outro cliente
                sock_active.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem de handshake para o outro cliente
                
            
                handshakeMsg            = sock_active.recv(1024)
                handshakeMsgDict        = json.loads(handshakeMsg)

                #Caso tenha recebido uma mensagem de handshake de sucesso do cliente passivo, cria uma nova thread para perfomar o canal de mensagens entre os dois
                self.lock.acquire()
                if(handshakeMsgDict['data']['userName'] != '' and handshakeMsgDict['data']['message'] == 'success'):
                    self.openChat[userInput[5:]] = 1
                    sock_active.setblocking(False)
                    sock_active.settimeout(0.5)
                    worker = threading.Thread(target=self.channelMessage, args=(handshakeMsgDict['data']['userName'], sock_active))
                    worker.start()

                self.lock.release()

            except Exception as e:
                traceback.print_exc()
                
                sock_active.close()
                response = {'method':'openChat', 'status': 'error', 'data':{'message': None} }
                return response
            finally:
                handshakeMsg = None

            response = {'method':'openChat', 'status': 'success', 'data':{'message': None} }
        else:
            response = {'method':'openChat', 'status': 'error', 'data':{'message': None} }
        
        return response
    
    def runAsPassive_P2P(self):
        """
            Representa o fluxo passivo da implementação P2P, para quando o cliente recebe uma proposta de conversa com outro cliente.
        """     
        
        inputs      = []
        sock        = socket.socket()   #Cria um socket para a comunicação
        sock.bind(('', self.myPort))    #Vincula a interface e porta para comunicação
        sock.listen(10)                 #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes
        sock.setblocking(False)         #Configura o sock para o modo não-bloqueante
        inputs.append(sock)             #Inclui o socket principal na lista de entradas de interesse
        
        try:
            while (True):
                read, write, exception = select.select(inputs, [], [])
                
                # Atualiza o cliente com as informações do servidor 
                response = self.handlerServerRequest(ACTIVE_USERS, None)
                self.handleServerResponse(OPEN_CHAT,response,None)
                
                for trigger in read:
                    #Caso o trigger seja um nova conexão e ainda não esteja setado para parar as threads associadas ao cliente
                    if (trigger == sock and self.status == 1 and not self.stopWorkers): 
                        try:                    
                            clientSock, ipAddress   = sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou. 
                            clientSock.setblocking(False) #Configura o sock para o modo não-bloqueante
                            clientSock.settimeout(0.5) #Define o tempo de espera por uma msg para 0.5 segundos

                            handshakeMsg            = clientSock.recv(1024)
                            self.lock.acquire()
                            handshakeMsgDict        = json.loads(handshakeMsg)

                            if((handshakeMsgDict['data']['userName'] != '') and (self.chatUsersStatus[handshakeMsgDict['data']['userName']] == '1') and ((not handshakeMsgDict['data']['userName'] in self.openChat)  or (handshakeMsgDict['data']['userName'] in self.openChat and self.openChat[handshakeMsgDict['data']['userName']] == 0))):

                                self.openChat[handshakeMsgDict['data']['userName']] = 1
                                chatUserName = handshakeMsgDict['data']['userName'] 
                                
                                handshakeMsgDict            =  {}
                                handshakeMsgDict['method']  = 'sendMessage'
                                handshakeMsgDict['data']    = {'userName':self.userName,'message':'success'}
                                handshakeMsg                = json.dumps(handshakeMsgDict, ensure_ascii=False) 
                                
                                #Envio da mensagem de handshake para o processo ativo e criação da thread que cuidará do canal de mensagens
                                clientSock.send(bytes(handshakeMsg,  encoding='utf-8')) 
                                self.lock.release()
                                self.clientView.refreshNotification(self.clientView.currScreen, f'{chatUserName} iniciou um chat com você! Digite "chat:{chatUserName} para abrir o chat."', add = True)
                                worker                                                       = threading.Thread(target=self.channelMessage, args=(chatUserName, clientSock))
                                worker.start()
                            else:
                                self.lock.release()
                                clientSock.close()
                            
                        except Exception as e:
                            print(e)
                            clientSock.close()
                            
                        finally:
                            handshakeMsg = None
                    else:
                        sock.close()
                        return

        except Exception as a:
            print(e)
            self.stop()

    def run(self):
        """
            Executa o fluxo principal do cliente. É a partir dele e dos comandos de entrada, sendo para o servidor ou para a própria aplicação, que são tomadas certas atitudes, inclusive criar novas threads para comunicações.
        """
        userInput, msg = self.clientView.homeScreen()
        while (userInput != EXIT):
            if(userInput == CREATE_ACCOUNT):
                userInput = self.clientView.createAccountScreen()
                response  = self.handlerServerRequest(CREATE_ACCOUNT, userInput)
                self.clientView.handlerResponse(response)

            elif(userInput == DELETE_ACCOUNT):
                userInput = self.clientView.deleteAccountScreen()
                response  = self.handlerServerRequest(DELETE_ACCOUNT, userInput)
                self.clientView.handlerResponse(response)

            elif(userInput == LOGIN):
                userInput = self.clientView.authScreen()
                response  = self.handlerServerRequest(LOGIN, userInput)
                self.handleInterfaceCommand(LOGIN, response=response)
                self.handleServerResponse(LOGIN, response, userInput)
                self.clientView.handlerResponse(response)
            
            elif(userInput == ACTIVE_USERS):
                response = self.handlerServerRequest(ACTIVE_USERS, None)
                self.clientView.handlerResponse(response)

            elif(userInput == ACTIVE_STATUS):
                response = self.handlerServerRequest(ACTIVE_STATUS, None)
                self.handleServerResponse(ACTIVE_STATUS,response,None)
                self.clientView.handlerResponse(response)
            
            elif(userInput == INACTIVE_STATUS):
                response = self.handlerServerRequest(INACTIVE_STATUS, None)
                self.handleServerResponse(INACTIVE_STATUS,response,None)
                self.clientView.handlerResponse(response)

            elif(userInput[0:5] == OPEN_CHAT):
                response = self.handleInterfaceCommand(OPEN_CHAT, userInput = userInput)
                self.clientView.handlerResponse(response)
            
            elif(userInput == LOGOUT):
                response = self.handlerServerRequest(LOGOUT, None)
                self.clientView.handlerResponse(response)
                result = self.handleServerResponse(LOGOUT,response,None)

            elif(userInput == CLOSE_CHAT):
                response = self.handleInterfaceCommand(CLOSE_CHAT)
                self.clientView.handlerResponse(response)
                
            elif(userInput == DELETE_MESSAGES):
                response = self.handleInterfaceCommand(DELETE_MESSAGES)
                self.clientView.handlerResponse(response)
            
            elif(userInput == SEND_MESSAGE):
                response = self.handleInterfaceCommand(SEND_MESSAGE, msg)

            userInput, msg = self.clientView.redirectScreen()
        
        self.stop()

if __name__ == '__main__':

    client = Client(serverHost='localhost', serverPort = 5000)
    client.run()
