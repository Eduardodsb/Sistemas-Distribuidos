import socket
import select
import threading
import json
import sys
import os
from clientInterface import ClientInterface
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS 

class Client:

    def __init__(self, serverHost='localhost', serverPort = 5000):
        self.serverHost = serverHost        #Endereço do processo passivo
        self.serverPort = serverPort        #Porta que o processo passivo estará escutando
        self.clientView = ClientInterface() #Inicializa a classe responsável pela interface da aplicação
        self.userName = ''
        self.password = ''
        self.status   = -1
        self.start()

    def start(self):
        self.sock = socket.socket()
        try:
            self.sock.connect((self.serverHost, self.serverPort)) #Abertura da conexão com o processo passivo
            #chamar tela 
        except Exception as e:
            # Colocar a tela responsável por dizer que a conexão foi fechada por erro inesperado ou algo do tipo...
            sys.exit(1)

    def __str__(self):
        pass

    def handlerServerRequest(self, method, userInput):
        methods = {CREATE_ACCOUNT: 'createAccount', DELETE_ACCOUNT: 'deleteAccount', LOGIN:'authAccount', ACTIVE_USERS:'getUsers', LOGOUT:'logout', EXIT:'logout', ACTIVE_STATUS:'setMyStatus', INACTIVE_STATUS:'setMyStatus'}

        if(method in (CREATE_ACCOUNT, DELETE_ACCOUNT, LOGIN)):
            userName, password = userInput
            request            = {'method':methods[method],'data':{'userName': userName,'password':password}}

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

        if(method == ACTIVE_STATUS and response['status'] == 'success'):
            self.status = 1
        
        if(method == INACTIVE_STATUS and response['status'] == 'success'):
            self.status = 0

        if(method == LOGOUT and response['status'] == 'success'):
            self.status = -1
        
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
            
            elif(userInput == LOGOUT):
                response = self.handlerServerRequest(LOGOUT, None)
                self.clientView.handlerResponse(response)
                result = self.handleServerResponse(LOGOUT,response,None)
                if(result):
                    break

            userInput = self.clientView.redirectScreen()
        
        self.handlerServerRequest(EXIT,None)
        self.stop()
        #threading.Thread(target=handlerServerRequest, args=(sock))

    def stop(self):
        self.sock.close()

if __name__ == '__main__':

    client = Client(serverHost='localhost', serverPort = 5000)
    client.run()
