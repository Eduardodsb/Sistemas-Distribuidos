
class User:

    def __init__(self, nickname, password, status, ip, port):
        self._nickname  = nickname
        self._password  = password
        self._status    = status
        self._ip        = ip
        self._port      = port
    
    def __str__(self):
        return '{' + '"nickname":"{}", "password":"{}", "status":{}, "ip":"{}", "port":{}'.format(self._nickname, self._password, self._status, self._ip, self._port) +'}'

    def __repr__(self):
        return self.__str__()

    def getNickname(self):
        return self._nickname
    
    def getPassword(self):
        return self._password
    
    def getStatus(self):
        return self._status
    
    def getIP(self):
        return self._ip

    def getPort(self):
        return self._port

    def setIP(ip):
        self._ip = ip

    def setPort(port):
        self._port = port

    def setStatus(status):
        self._status = status


if __name__ == '__main__':
    test = User("tatalimpink", "1234", 0, "111.111.11", 1200)

    print(test.getNickname())

