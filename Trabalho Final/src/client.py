import socket
import select
import threading
import json
import sys
import traceback
import os
import random
from clientInterface import ClientInterface

from constants import CREATE_CHANNEL, SUBSCRIBE_CHANNEL, UNSUBSCRIBE_CHANNEL, SHOW_MY_SUBS, PUBLISH_CHANNEL, SHOW_MY_CHANNELS, SHOW_ALL_CHANNELS
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT 
from constants import HOME_SCR, CREATE_ACCOUNT_SCR, DELETE_ACCOUNT_SCR, LOGIN_SCR, PRINCIPAL_MENU_SCR

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
        self.channelMessages    = []                #Guarda as menssagens recebidas de cada canal
        self.fifoMessages       = {}                #Fila de envio de mensagens trocadas entre usuários. Ex:{'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.lock               = threading.Lock()  #Inicializa o lock
        self.start()                                #Adquire o socket e se conecta com o servidor

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
    
    def recvByMethod(self, notify = False):
        """
            Aguarda pela mensagem que apresenta a tag de interesse
            :param notify: especifica se a mensagem é uma notificação ou não
            :return mensagem que apresenta a tag de interesse
        """
        size = 1024
        peeked_msg      = self.sock.recv(size, socket.MSG_PEEK)
        peeked_response = json.loads(peeked_msg)

        while(not notify and (peeked_response['method'] == 'notifySubscriber')):
            peeked_msg      = self.sock.recv(size, socket.MSG_PEEK)
            peeked_response = json.loads(peeked_msg)

        while(notify and (peeked_response['method'] != 'notifySubscriber')):
            peeked_msg      = self.sock.recv(size, socket.MSG_PEEK)
            peeked_response = json.loads(peeked_msg)
        
        msg_w_my_method = self.sock.recv(1024)
        return msg_w_my_method

    def handlerServerRequest(self, method, userInput):
        """
            Dado o método e o input do cliente, gera a mensagem de requisição para o servidor e envia para o mesmo.
            :param method: comando a ser executado.
            :param userInput: entradas digitadas pelo cliente.
            :return mensagem de resposta do servidor.
        """
        methods = {CREATE_ACCOUNT: 'createAccount', DELETE_ACCOUNT: 'deleteAccount', LOGIN:'authAccount',  LOGOUT:'logout', CREATE_CHANNEL:'createChannel', SUBSCRIBE_CHANNEL: 'subscribeChannel', UNSUBSCRIBE_CHANNEL:'unsubscribeChannel', SHOW_MY_SUBS:'showMySubscriptions', PUBLISH_CHANNEL:'publishChannel', SHOW_MY_CHANNELS:'showMyOwnChannels', SHOW_ALL_CHANNELS:'showAllChannels'}

        if(method in (CREATE_ACCOUNT, DELETE_ACCOUNT, LOGIN)):
            userName, password = userInput
            request            = {'method':methods[method],'data':{'userName': userName,'password':password}}

        elif(method == PUBLISH_CHANNEL):
            channelName = userInput[1][0]
            message = userInput[1][1]
            request = {'method':methods[method],'data':{'userName': self.userName,'password': self.password, 'channelName': channelName, 'message': message}}

        elif(method in (SUBSCRIBE_CHANNEL, UNSUBSCRIBE_CHANNEL, CREATE_CHANNEL)):
            channelName = userInput[1]
            request = {'method':methods[method], 'data': {'userName': self.userName,'password': self.password,'channelName': channelName }}
        
        elif(method in (LOGOUT, SHOW_MY_SUBS, SHOW_MY_CHANNELS)):
            request = {'method':methods[method], 'data': {'userName': self.userName,'password': self.password}}
        
        elif(method == SHOW_ALL_CHANNELS):
            request = {'method':methods[method]}

        request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor
        self.sock.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o servidor
             
        response_msg = self.recvByMethod()      #Recebimento da mensagem enviada pelo servidor.
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

            work = threading.Thread(target= self.runChannelListener, args=())
            work.daemon = True # Kill threads when the main program exits
            work.start()
        
        #Quando um usuário se desloga, é necessário trocar seu status para offline e terminar suas threads trabalhadoras associadas assim como o fluxo passivo
        if(method == LOGOUT and response['status'] == 'success'): 
            self.finishBusiness()

    def handleInterfaceCommand(self, cmd, userInput = None, response = None):
        """
            Dado o comando enviado e outras possíveis informações (entrada do usuário ou resposta a requisição), trata os comandos da interface.
            :param cmd: comando a ser executado.
            :param userInput: entradas digitadas pelo cliente.
            :param response: mensagem de resposta (dicionário).
            :return void ou mensagem de resposta (dicionário) para a classe clientInterface.
        """

        #Ao se logar, deve-se atualizar as informações dos usuários cadastrados na aplicação 
        if(cmd == LOGIN and (response['status'] == 'success')):
            self.stopWorkers    = False
            response            = None
        
        if(cmd == SHOW_MY_SUBS and (response['status'] == 'success')):
            list_of_subs = response['data']
            self.clientView.responsesToPrint.append("Canais em que você está inscrito: " + ", ".join(list_of_subs) + "\n")

        if(cmd == SHOW_MY_CHANNELS and (response['status'] == 'success')):
            list_of_channels = response['data']
            self.clientView.responsesToPrint.append("Canais em que você é proprietário: " + ", ".join(list_of_channels) + "\n")

        if(cmd == SHOW_ALL_CHANNELS and (response['status'] == 'success')):
            list_of_channels = response['data']
            self.clientView.responsesToPrint.append("Canais registrados no servidor: " + ", ".join(list_of_channels) + "\n")
 
        return None

    def runChannelListener(self):
        """
            Representa o fluxo ouvinte do cliente que ficará atento a quaisquer atualizações dos canais inscritos.
        """       
        request_msg = None

        try:
            while True:
                try:
                    #Recebe a mensagens dos canais
                    request_msg = self.recvByMethod(notify = True) 
                except socket.timeout as e:
                    pass
                
                #Entra se receber logout ou o servidor cair
                if(request_msg == b'' or self.stopWorkers): 
                    break

                if(request_msg != None):
                    request = json.loads(request_msg)   
                    channelName = request['data']['channelName']             

                    self.lock.acquire()
                    #Salva a mensagem recebida na lista de mensagens com aquele canal
                    self.channelMessages.append(channelName + ":" + request['data']['message'])
                    self.lock.release()
                
                self.lock.acquire()
                self.clientView.messages_queue = self.channelMessages
                self.clientView.printPrincipalMenuScreen()
                self.lock.release()

                request_msg = None
                
        except Exception as e:
            self.sock.close()
    
    def run(self):
        """
            Executa o fluxo principal do cliente. É a partir dele e dos comandos de entrada, sendo para o servidor ou para a própria aplicação, que são tomadas certas atitudes, inclusive criar novas threads para comunicações.
        """

        userInput = self.clientView.homeScreen()
        while (userInput[0] != EXIT):
            if(userInput[0] == CREATE_ACCOUNT):
                credentials = self.clientView.createAccountScreen()
                response    = self.handlerServerRequest(CREATE_ACCOUNT, credentials)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == DELETE_ACCOUNT):
                credentials = self.clientView.deleteAccountScreen()
                response    = self.handlerServerRequest(DELETE_ACCOUNT, credentials)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == LOGIN):
                credentials = self.clientView.authScreen()
                response    = self.handlerServerRequest(LOGIN, credentials)
                self.handleInterfaceCommand(LOGIN, response=response)
                self.handleServerResponse(LOGIN, response, credentials)
                self.clientView.handlerResponse(response)
            
            elif(userInput[0] == LOGOUT):
                response = self.handlerServerRequest(LOGOUT, None)
                self.clientView.handlerResponse(response)
                result   = self.handleServerResponse(LOGOUT,response,None)
           
            elif(userInput[0] == PUBLISH_CHANNEL):
                response = self.handlerServerRequest(PUBLISH_CHANNEL, userInput)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == SUBSCRIBE_CHANNEL):
                response = self.handlerServerRequest(SUBSCRIBE_CHANNEL, userInput)
                self.clientView.handlerResponse(response)
                
            elif(userInput[0] == UNSUBSCRIBE_CHANNEL):
                response = self.handlerServerRequest(UNSUBSCRIBE_CHANNEL, userInput)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == SHOW_MY_SUBS):
                response = self.handlerServerRequest(SHOW_MY_SUBS, userInput)
                self.handleInterfaceCommand(SHOW_ALL_CHANNELS, userInput, response)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == SHOW_MY_CHANNELS):
                response = self.handlerServerRequest(SHOW_MY_CHANNELS, userInput)
                self.handleInterfaceCommand(SHOW_ALL_CHANNELS, userInput, response)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == SHOW_ALL_CHANNELS):
                response = self.handlerServerRequest(SHOW_ALL_CHANNELS, userInput)
                self.handleInterfaceCommand(SHOW_ALL_CHANNELS, userInput, response)
                self.clientView.handlerResponse(response)

            elif(userInput[0] == CREATE_CHANNEL):
                response = self.handlerServerRequest(CREATE_CHANNEL, userInput)
                self.clientView.handlerResponse(response)

            userInput = self.clientView.redirectScreen()
        
        self.stop()

if __name__ == '__main__':

    client = Client(serverHost='localhost', serverPort = 5000)
    client.run()
