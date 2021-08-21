
class User:

    def __init__(self, userName, password, status, ip, port):
        self._userName  = userName
        self._password  = password
        self._status    = status
        self._ip        = ip
        self._port      = port
    
    def __str__(self):
        return '{' + ' userName":"{}", "password":"{}", "status":{}, "ip":"{}", "port":{}'.format(self._userName, self._password, self._status, self._ip, self._port) +'}'
    
    def __str__(self, userName = True, password = True, status = True, ip = True, port = True):
        return '{' + ('"userName":"'+ self._userName + '",' if userName else "" ) + ('"password":"'+ self._password + '",' if password else "" ) + ('"status":"'+ str(self._status) + '",' if status else "" ) + ('"ip":"'+ self._ip + '",' if ip else "" ) + ('"port":'+ str(self._port) if port else "" ) +'}'

    def __repr__(self):
        return self.__str__()

    def getUserName(self):
        return self._userName
    
    def getPassword(self):
        return self._password
    
    def getStatus(self):
        return self._status
    
    def getIP(self):
        return self._ip

    def getPort(self):
        return self._port

    def setIP(self, ip):
        self._ip = ip

    def setPort(self, port):
        self._port = port

    def setStatus(self,status):
        self._status = status


if __name__ == '__main__':
    test = User("tatalimpink", "1234", 0, "111.111.11", 1200)

    print(test.__str__(True, True, False, False, True))

