from dataLayer import DataLayer
from user import User
import threading
import json

##### Messages returned constant variables
INTERNAL_ERROR_SERVER   = 'Erro interno no servidor'
INVALID_CREDENTIALS     = 'Credencial inválida'
AUTHENTICATION_SUCCESS  = 'Logado com sucesso'
LOGOUT_ERROR            = 'Não foi possível realizar o logout'
METHOD_NOT_FOUND        = 'Método não encontrado'
INVALID_STATUS          = 'Status inválido'
DELETE_SUCCESS          = 'Deletado com sucesso'
CREATE_SUCCESS          = 'Criado com sucesso'
DESCONNECTED_SUCCESS    = 'Desconectado com sucesso'

class ProcessLayer:

    #ProcessLayer.lock para acesso do dicionario 'conexoes'
    lock        = threading.Lock()
    datalayer   = None
    users       = {}

    def __init__(self):
        ProcessLayer.datalayer   = DataLayer("dataBase.json")

    def readUsers(self):
        try:
            ProcessLayer.users = ProcessLayer.datalayer.readUsers()
        except Exception as e:
            print(e)

    def saveUsers(self):
        try:
            ProcessLayer.lock.acquire()
            print(ProcessLayer.users)
            ProcessLayer.datalayer.writeUsers(ProcessLayer.users)
            ProcessLayer.lock.release()
        except Exception as e:
            print(e)
    
    def logoutClient(self, userName, password):
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                ProcessLayer.users[userName].setStatus(-1)
                ProcessLayer.users[userName].setIP('')
                ProcessLayer.users[userName].setPort(0)
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
        try:
            ProcessLayer.lock.acquire()
            if(userName not in ProcessLayer.users):
                ProcessLayer.users[userName] = User(userName, password, -1,'',0)
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
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                ProcessLayer.users[userName] = User(userName, password, -1,'',0)
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
        ip, port = ipAddress
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                ProcessLayer.users[userName].setStatus(1)
                ProcessLayer.users[userName].setIP(ip)
                ProcessLayer.users[userName].setPort(port)
                response = {'status':'success', 'method':'authAccount', 'data': {'message': AUTHENTICATION_SUCCESS}}
            else:
                response = {'status':'error', 'method':'authAccount', 'data': {'message': INVALID_CREDENTIALS}}

        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'authAccount', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def getClientStatus(self,  userName, password):
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                response = {'status':'success', 'method':'getMyStatus','data': {'message': ProcessLayer.users[userName].getStatus()}}
            else:
                response = {'status':'error', 'method':'getMyStatus', 'data': {'message': INTERNAL_ERROR_SERVER}}

        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'getMyStatus', 'data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def setClientStatus(self, userName, password, status):
        try:
            ProcessLayer.lock.acquire()
            if(userName in ProcessLayer.users and ProcessLayer.users[userName].getPassword() == password):
                if(status == 1 or status == 0):
                    ProcessLayer.users[userName].setStatus(status)
                    response = {'status':'success', 'method':'setMyStatus','data': {'message': f'Status {status} definido com sucesso.'}}
                else:
                    response = {'status':'error', 'method':'setMyStatus','data': {'message': INVALID_STATUS}}           
            else:
                response = {'status':'error', 'method':'setMyStatus','data': {'message':INVALID_CREDENTIALS}}           
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'setMyStatus','data': {'message': INTERNAL_ERROR_SERVER}}
        finally:
            ProcessLayer.lock.release()
            return response

    def getUsersList(self):
        result = []
        try:
            for key, value in ProcessLayer.users.items():
                result.append(json.loads(value.__str__(userName=True, password=False, status=True, ip=True, port=True)))

            response = {'status':'success', 'method':'getUsers','data':result}
        except Exception as e:
            print(e)
            response = {'status':'error', 'method':'getUsers','data': {'message': INTERNAL_ERROR_SERVER}}

        return response
            
    def methodNotFound(self, _method):
        return {'status':'error', 'method':_method,'data': {'message': METHOD_NOT_FOUND}} 


if __name__ == '__main__':
    pass

