import socket
import select
import threading
import json
import sys
import os
from clientInterface import ClientInterface
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS, OPEN_CHAT, CLOSE_CHAT, DELETE_MESSAGES, OPEN_HIST_MESSAGES, CLOSE_HIST_MESSAGES, SEND_MESSAGE

class Client:

    def __init__(self, serverHost='localhost', serverPort = 5000):
        self.serverHost         = serverHost        #Endereço do processo passivo
        self.serverPort         = serverPort        #Porta que o processo passivo estará escutando
        self.myPort             = None              #Porta que o cliente irá receber as conexões de outros clientes
        self.clientView         = ClientInterface() #Inicializa a classe responsável pela interface da aplicação
        self.userName           = ''
        self.password           = ''
        self.status             = -1
        self.chatUsersIps       = {} #Ips dos usuários cadastrados no sistema
        self.chatUsersPorts     = {} #Portas dos usuários cadastrados no sistema
        self.chatUsersStatus    = {} #Status dos usuários cadastrados no sistema
        self.openChat           = {} #Usuários com os quais se mantém a conversa ativa
        self.openChatMessages   = {} # {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.fifoMessages       = {} # {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.lock               = threading.Lock()
        self.start()

    def __str__(self):
        pass

    def scanPort(self):

        ip = socket.gethostbyname(socket.gethostname())

        for port in range(2000,65535):
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
        self.sock = socket.socket()
        try:
            self.sock.connect((self.serverHost, self.serverPort)) #Abertura da conexão com o processo passivo
            #chamar tela 
        except Exception as e:
            # Colocar a tela responsável por dizer que a conexão foi fechada por erro inesperado ou algo do tipo...
            sys.exit(1)

    def handlerServerRequest(self, method, userInput):
        methods = {CREATE_ACCOUNT: 'createAccount', DELETE_ACCOUNT: 'deleteAccount', LOGIN:'authAccount', ACTIVE_USERS:'getUsers', LOGOUT:'logout', EXIT:'logout', ACTIVE_STATUS:'setMyStatus', INACTIVE_STATUS:'setMyStatus'}

        if(method in (CREATE_ACCOUNT, DELETE_ACCOUNT, LOGIN)):
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
        self.sock.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o processo passivo
        
        response_msg = self.sock.recv(1024) #Recebimento da mensagem enviada pelo processo passivo. OBS: chamada pode ser bloqueante e o argumento indica o tamanho máximo de bytes da msg.
        response     = json.loads(response_msg) #Tranformar a mensagem recebida em um dicionário.

        return response

    def handleServerResponse(self, method, response, userInput):
        
        if(method == LOGIN and response['status'] == 'success'):
            userName, password = userInput
            self.userName      = userName
            self.password      = password
            self.status        = 1
            work = threading.Thread(target= self.runAsPassive_P2P, args=())
            work.start()

        if(method == ACTIVE_STATUS and response['status'] == 'success'):
            self.status = 1
        
        if(method == INACTIVE_STATUS and response['status'] == 'success'):
            self.status = 0

        if(method == LOGOUT and response['status'] == 'success'):
            self.status = -1

        if(method == OPEN_CHAT and response['status'] == 'success'):
            self.lock.acquire()
            for element in response['data']:
                self.chatUsersIps[element['userName']]       = element['ip']
                self.chatUsersPorts[element['userName']]     = element['port']
                self.chatUsersStatus[element['userName']]    = element['status']
            self.lock.release()
            print(self.chatUsersStatus)
            response = {'method':'openChat', 'status': 'success', 'data':{'message': None} }
            return response
        
        elif(method == OPEN_CHAT and response['status'] == 'error'):
            response = {'method':'openChat', 'status': 'error', 'data':{'message': None} }
            return response

    def channelMessage(self, chatUserName, clientSock):
        request_msg = None
        while True:
            try:
                request_msg = clientSock.recv(1024) #Recebe a mensagem do processo ativo
            except socket.timeout as e:
                pass

            if(request_msg == b''): #Entra se receber logout ou esse cara
                self.lock.acquire()
                self.openChat[chatUserName] = 0
                self.lock.release()
                clientSock.close()
                break

            if(request_msg != None):
                #Mensagem de confirmação de recebimento de requisição
                notifyReceivementMsg = {'method': 'sendMessage', 'status': 'success', 'data': None}
                notifyReceivement = json.dumps(notifyReceivementMsg, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
                clientSock.send(bytes(notifyReceivement,  encoding='utf-8')) #Envio da mensagem para o processo passivo
                
                if(request['method'] == 'logout'):
                    self.lock.acquire()
                    self.openChat[chatUserName] = 0
                    self.lock.release()
                    clientSock.close()
                    break

                self.lock.acquire()
                self.openChatMessages[chatUserName].append(chatUserName + ":" + request['data']['message'])
                self.lock.release()
                
            self.lock.acquire()
            for i in len(self.fifoMessages[chatUserName]):
                msg = self.fifoMessages[chatUserName][0] # {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}    
                request = {'method': 'sendMessage', 'data':{'userName': self.userName, 'message': msg}}
                request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
                clientSock.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o processo passivo
                
                clientSock.setblocking(True)
                request_msg = clientSock.recv(1024) #Recebe a mensagem do processo ativo
                if(request_msg == b''): #Entra se receber logout ou esse cara
                    self.lock.acquire()
                    self.openChat[chatUserName] = 0
                    self.lock.release()
                    clientSock.close()
                    break
                
                request = json.loads(request_msg)
                if(request['status'] == 'success'):
                    self.fifoMessages[chatUserName].pop(0)
            self.lock.release()

            clientSock.setblocking(False)
            clientSock.settimeout(10.0)
            request_msg = None
    
    def runAsActive_P2P(self, userInput):
        if(userInput[:5] == OPEN_CHAT and self.status == 1 and self.chatUsersStatus[userInput[5:]] == '1'
        and ((not userInput[5:] in self.openChat)  or (userInput[5:] in self.openChat and self.openChat[userInput[5:]] == 0))):
            try:

                sock_active = socket.socket()
                sock_active.connect((self.chatUsersIps[userInput[5:]], self.chatUsersPorts[userInput[5:]])) #Abertura da conexão com o processo passivo
                sock_active.setblocking(True) #Configura o sock para o modo não-bloqueante
                print( 'aqui', self.userName)
                request     = {'method': 'sendMessage', 'data':{'userName': self.userName, 'message': 'hand shake'}}
                request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
                sock_active.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o processo passivo
                
                
                handshakeMsg            = sock_active.recv(1024)
                print(handshakeMsg)
                handshakeMsgDict        = json.loads(handshakeMsg)
                print('aqui 3 ')
                self.lock.acquire()
                if(handshakeMsgDict['data']['userName'] != '' and handshakeMsgDict['data']['message'] == 'success'):
                    worker = threading.Thread(target=self.channelMessage, args=(handshakeMsgDict['data']['userName'], sock_active))
                    worker.start()

                self.lock.release()

            except Exception as e:
                print(e)
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
        inputs      = []
        blocking    = False
        sock        = socket.socket() #Cria um socket para a comunicação
        sock.bind(('', self.myPort)) #Vincula a interface e porta para comunicação
        sock.listen(10)  #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes
        sock.setblocking(blocking) #Configura o sock para o modo não-bloqueante
        inputs.append(sock) #Inclui o socket principal na lista de entradas de interesse
        
        try:
            while (True):
                read, write, exception = select.select(inputs, [], [])
            
                for trigger in read:
                    if (trigger == sock and self.status == 1): #Caso o trigger seja um nova conexão
                        try:                    
                            clientSock, ipAddress   = sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou. OBS: A chamada pode ser bloqueante
                            clientSock.setblocking(False)
                            clientSock.settimeout(10.0)

                            handshakeMsg            = clientSock.recv(1024)
                            self.lock.acquire()
                            handshakeMsgDict        = json.loads(handshakeMsg)
                            print(self.chatUsersStatus)
                            if((handshakeMsgDict['data']['userName'] != '') and (self.chatUsersStatus[handshakeMsgDict['data']['userName']] == '1') and ((not handshakeMsgDict['data']['userName'] in self.openChat)  or (handshakeMsgDict['data']['userName'] in self.openChat and self.openChat[handshakeMsgDict['data']['userName']] == 0))):
                                print('hoho')
                                self.openChat[handshakeMsgDict['data']['userName']]         = 1
                                chatUserName = handshakeMsgDict['data']['userName'] 
                                self.openChatMessages[handshakeMsgDict['data']['userName']] = []# {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
                                
                                handshakeMsgDict                                            =  {}
                                handshakeMsgDict['method']                                  = 'sendMessage'
                                handshakeMsgDict['data']                                    = {'userName':self.userName,'message':'success'}
                                handshakeMsg                                                = json.dumps(handshakeMsgDict, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
                                
                                print(handshakeMsgDict)
                                print(handshakeMsg)
                                clientSock.send(bytes(handshakeMsg,  encoding='utf-8')) #Envio da mensagem para o processo passivo
                                self.lock.release()
                                worker                                                       = threading.Thread(target=self.channelMessage, args=(chatUserName. clientSock))
                                worker.start()
                                print('show')
                            else:
                                self.lock.release()
                                clientSock.close()
                            
                        except Exception as e:
                            print(e)
                            clientSock.close()
                            
                        finally:
                            handshakeMsg = None
        except Exception as a:
            print(e)
            self.stop()

    def run(self):

        userInput = self.clientView.homeScreen()
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
                response = self.handlerServerRequest(ACTIVE_USERS, None)
                response = self.handleServerResponse(OPEN_CHAT,response,None)
                if(response['status'] == 'success'):
                    response = self.runAsActive_P2P(userInput)
                self.clientView.handlerResponse(response)
                
                #Chamar a janela de chat com fulaninho

            elif(userInput == LOGOUT):
                response = self.handlerServerRequest(LOGOUT, None)
                self.clientView.handlerResponse(response)
                result = self.handleServerResponse(LOGOUT,response,None)
                if(result):
                    break

            userInput = self.clientView.redirectScreen()
        
        self.handlerServerRequest(EXIT,None)
        self.stop()

    def stop(self):
        self.sock.close()

if __name__ == '__main__':

    client = Client(serverHost='localhost', serverPort = 5000)
    client.run()
