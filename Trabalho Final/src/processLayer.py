from dataLayer import DataLayer
from user import User
from channel import Channel
import threading
import json

##### Messages returned constant variables
INTERNAL_ERROR_SERVER   = 'Erro interno no servidor'
INVALID_CREDENTIALS     = 'Credencial inválida'
ALREADY_LOGGED          = 'Você já está logado em outra sessão'
AUTHENTICATION_SUCCESS  = 'Logado com sucesso'
LOGOUT_ERROR            = 'Não foi possível realizar o logout'
METHOD_NOT_FOUND        = 'Método não encontrado'
INVALID_STATUS          = 'Status inválido'
DELETE_SUCCESS          = 'Deletado com sucesso'
CREATE_SUCCESS          = 'Criado com sucesso'
DESCONNECTED_SUCCESS    = 'Desconectado com sucesso'
CHANNEL_ALREADY_EXITS   = 'Canal já existe'
SUBSCRIBED_SUCESS       = 'Inscrito com sucesso'
UNSUBSCRIBED_SUCESS     = 'Desinscrito com sucesso'
PUBLISHED_SUCCESS       = 'Mensagem pulicada com sucesso'

class ProcessLayer:
    """
        Classe destinada à camada de processamento
    """
    
    #ProcessLayer.lock para acesso do dicionario 'conexoes'
    lock        = threading.Lock() #Incializa o lock
    datalayer   = None
    users       = {}
    usersLogged = {}
    channels    = {}
    
    def __init__(self):
        ProcessLayer.datalayer   = DataLayer("userDatabase.json", "channelDatabase.json")

        
    def readUsers(self):
        """
            Responsável pela leitura dos dados do usuário
        """  
        try:
            ProcessLayer.users = ProcessLayer.datalayer.readUsers()
        except Exception as e:
            print(e)

    def saveUsers(self):
        """
            Responsável por salva os dados dos usuários 
        """  
        try:
            ProcessLayer.lock.acquire()
            ProcessLayer.datalayer.writeUsers(ProcessLayer.users)
            ProcessLayer.lock.release()
        except Exception as e:
            print(e)

    def readChannels(self):
        """
            Responsável pela leitura dos dados dos canais
        """  
        try:
            ProcessLayer.users = ProcessLayer.datalayer.readChannels()
        except Exception as e:
            print(e)

    def saveChannels(self):
        """
            Responsável por salvar os dados dos canais.
        """  
        try:
            ProcessLayer.lock.acquire()
            ProcessLayer.datalayer.writeChannels(ProcessLayer.channels)
            ProcessLayer.lock.release()
        except Exception as e:
            print(e)
    
    def logoutClient(self, userName, password):
        """
            Desloga o cliente/usuário da aplicação
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                ProcessLayer.usersLogged.pop(userName)
                response = {'status':'success', 'method':'logout', 'data': {'message': DESCONNECTED_SUCCESS}}
            else:
                response = {'status':'error', 'method':'logout', 'data': {'message': LOGOUT_ERROR}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'logout', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response
    
    def createClientAccount(self, userName, password):
        """
            Responsável pela criação de novos clientes/usuários no sistema
            :param userName: user name do cliente/usuário
            :param password: senha escolhida pelo cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try:
            ProcessLayer.lock.acquire()
            if(userName not in ProcessLayer.users):
                ProcessLayer.users[userName] = User(userName, password, [], [])
                response = {'status':'success', 'method':'createAccount', 'data': {'message': CREATE_SUCCESS}}
            else:
                response = {'status':'error', 'method':'createAccount', 'data': {'message': INTERNAL_ERROR_SERVER}}           
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'createAccount', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def deleteClientAccount(self, userName, password):
        """
            Deleta o cliente/usuário da aplicação
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                myChannels = []
                for chName, chObj in ProcessLayer.channels.items(): # Para cada canal do sistema 
                    if userName in chObj.getSubscribedUsers(): # Verifica se o usuário que vai deletar conta está inscrito nele
                        chObj.unsubscribeUser(userName) # Se sim, desinscreve o usuário dele

                    if userName == chObj.getOwner(): # Verifica se o usuário que vai deletar conta é dono dele
                        myChannels.append(chName) # Guarda o nome do canal que ele é dono
                        
                        # Remove todos os usuários inscritos no canal do dono
                        for uName, userObj in ProcessLayer.users.items():
                            if chName in userObj.getSubscribedChannels():
                                userObj.removeSubscription(chName)
                      
                # Remove os canais do dono da listagem de canais
                for ch in myChannels:
                    ProcessLayer.channels.pop(ch)

                ProcessLayer.users.pop(userName)
                
                response = {'status':'success', 'method':'deleteAccount', 'data': {'message': DELETE_SUCCESS}}
            else:
                response = {'status':'error', 'method':'deleteAccount', 'data': {'message': INVALID_CREDENTIALS}}           
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'deleteAccount', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def authClientAccount(self, userName, password, ipAddress):
        """
            Realiza a autenticação do usuário.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :param ipAddress:  ip e porta do cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        ip, port = ipAddress
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                ProcessLayer.usersLogged[userName] = ProcessLayer.users[userName]
                response = {'status':'success', 'method':'authAccount', 'data': {'message': AUTHENTICATION_SUCCESS}}
            else:
                response = {'status':'error', 'method':'authAccount', 'data': {'message': INVALID_CREDENTIALS}}

        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'authAccount', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def createChannel(self, userName, password, channelName): 
        """
            Realiza a criação de um canal.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :param channelName:  nome do canal
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try:
            if (channelName not in ProcessLayer.channels) :
                ch = Channel(userName, channelName)                      # Cria um novo canal
                ProcessLayer.channels[channelName] = ch                  # Atualiza a lista de canais com o novo canal
                ProcessLayer.users[userName].addOwnChannel(channelName)  # Adiciona o novo canal na lista de canais em que o usuário é dono
                response = {'status':'success', 'method':'createChannel', 'data': {'message': CREATE_SUCCESS}}
            else:
                response = {'status':'error', 'method':'createChannel', 'data': {'message': CHANNEL_ALREADY_EXITS}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'createChannel', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response
            
    def subscribeChannel(self, userName, password, channelName):
        """
            Realiza a subscrição do usuário.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :param channelName:  nome do canal
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try: 
            userAuthenticated = userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password
            existChannel      = channelName in ProcessLayer.channels
            userNotOwner      = ProcessLayer.channels[channelName].getOwner() != userName
            userNotSubscribed = userName not in ProcessLayer.channels[channelName].getSubscribedUsers()
            
            if (userAuthenticated and existChannel and userNotOwner and  userNotSubscribed):
                ProcessLayer.users[userName].addSubscribedChannels(channelName)
                ProcessLayer.channels[channelName].subscribeUser(userName)
                response = {'status':'success', 'method':'subscribeChannel', 'data': {'message': SUBSCRIBED_SUCESS}}
            else:
                response = {'status':'error', 'method':'subscribeChannel', 'data': {'message': INTERNAL_ERROR_SERVER}}
                
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'subscribeChannel', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response

    def unsubscribeChannel(self, userName, password, channelName):
        """
            Função para desincrever um usuário de um canal.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :param channelName: nome do canal
            :return retorna a mensagem de resposta da requisição de execução do comando
        """ 
        try:
            userAuthenticated   = userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password
            existChannel        = channelName in ProcessLayer.channels
            userNotOwner        = ProcessLayer.channels[channelName].getOwner() != userName
            userSubscribed      = userName in ProcessLayer.channels[channelName].getSubscribedUsers()

            if (userAuthenticated and existChannel and userNotOwner and userSubscribed):
                ProcessLayer.users[userName].removeSubscription(channelName)
                ProcessLayer.channels[channelName].unsubscribeUser(userName)                
                response = {'status':'success', 'method':'unsubscribeChannel', 'data': {'message': UNSUBSCRIBED_SUCESS}}
            else:
                response = {'status':'error', 'method':'unsubscribeChannel', 'data': {'message': INTERNAL_ERROR_SERVER}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'unsubscribeChannel', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response

    def showMySubscriptions(self, userName, password):
        """
            Função para mostrar quais canais um usuário está inscrito.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """ 
        try:
            userAuthenticated = userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password
            
            if (userAuthenticated):
                result = ProcessLayer.users[userName].getSubscribedChannels()
                response = {'status':'success', 'method':'showMySubscriptions', 'data': result}
            else:
                response = {'status':'error', 'method':'showMySubscriptions', 'data': {'message': INVALID_CREDENTIALS}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'showMySubscriptions', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response

    def showMyOwnChannels(self, userName, password):
        """
            Função para mostrar quais canais que o usuário é dono.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :return retorna a mensagem de resposta da requisição de execução do comando
        """  
        try:
            userAuthenticated = userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password
            if (userAuthenticated):
                result = ProcessLayer.users[userName].getOwnChannels()
                response = {'status':'success', 'method':'showMyOwnChannels', 'data': {'message': result}}
            else:
                response = {'status':'error', 'method':'showMyOwnChannels', 'data': {'message': INVALID_CREDENTIALS}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'showMyOwnChannels', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response

    def showAllChannels(self):
        """
            Retorna todos os canais existentes no servidor
            :return retorna a mensagem de resposta da requisição de execução do comando
        """ 
        try:
            result   = list(ProcessLayer.channels.keys())
            response = {'status':'success', 'method':'showAllChannels', 'data': result}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'showAllChannels', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response

    def publishChannel(self, userName, message, channelName):
        """
            Publica uma mensagem em um canal.
            :param userName: user name do cliente/usuário
            :param password: senha do cliente/usuário
            :param channelName: nome do canal em que a mensagem será publicada
            :return retorna a mensagem de resposta da requisição de execução do comando
        """         
        try:
            userAuthenticated = userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password
            userOwner         = ProcessLayer.channels[channelName].getOwner() == userName

            if (userAuthenticated and userOwner):
                ProcessLayer.channels[channelName].publishMessage(message)                
                # ---- send mensage to subscribers -----
                response = {'status':'success', 'method':'showAllChannels', 'data': {'message': PUBLISHED_SUCCESS}}
            else:
                response = {'status':'error', 'method':'showAllChannels', 'data': {'message': INTERNAL_ERROR_SERVER}}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'showAllChannels', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            return response
       
    def methodNotFound(self, _method):
        """
            Função chave chamada quando é tentado executar um método que não existe na aplicação.
            :param _method: método passado
            :return retorna a mensagem de resposta da requisição de execução do comando
        """         
        return {'status':'error', 'method':_method,'data': {'message': METHOD_NOT_FOUND}} 


if __name__ == '__main__':
    pass

