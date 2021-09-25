
class User:

    def __init__(self, userName, password, ownChannels = [], subscribedChannels = []):
        self._userName              = userName
        self._password              = password
        self._ownChannels           = ownChannels
        self._subscribedChannels    = subscribedChannels

    def __str__(self):
        strOwnChannels = '["'+ str("\",\"".join(self._ownChannels)) + '"]' if self._ownChannels else '[]'
        strSubscribedChannels = '["'+ str("\",\"".join(self._subscribedChannels)) + '"]' if self._subscribedChannels else '[]'
        return '{' + ' "userName":"{}", "password":"{}", "ownChannels":{}, "subscribedChannels":{}'.format(self._userName, self._password, strOwnChannels, strSubscribedChannels)  +'}'
    
    #def __str__(self, userName = True, password = True, ownChannels = True, subscribedChannels = True):
    #    return '{' + ('"userName":"'+ self._userName + '",' if userName else "" ) + ('"password":"'+ self._password + '",' if password else "" ) + ('"ownChannels":[\"'+ str("\",\"".join(self._ownChannels)) + '\"],' if ownChannels else "" ) + ('"subscribedChannels":[\"'+ str("\",\"".join(self._subscribedChannels)) + '\"]' if subscribedChannels else "" ) +'}'

    def __repr__(self):
        return self.__str__()

    def getUserName(self):
        return self._userName
    
    def getPassword(self):
        return self._password
    
    def getOwnChannels(self):
        return self._ownChannels
    
    def getSubscribedChannels(self):
        return self._subscribedChannels

    def setOwnChannels(self, ownChannels):
        self._ownChannels = ownChannels

    def setSubscribedChannels(self, subscribedChannels):
        self._subscribedChannels = subscribedChannels

    def addOwnChannel(self, channelName):
        self._ownChannels.append(channelName)
    
    def removeOwnChannel(self, channelName):
        self._ownChannels.remove(channelName)
    
    def addSubscribedChannels(self, channelName):
        self._subscribedChannels.append(channelName)

    def removeSubscription(self, channelName):
        self._subscribedChannels.remove(channelName)

if __name__ == '__main__':
    test = User("nickname", "1234", ['a', 'b'], ['c'])
    #print(test.__str__(True, True, True, True))
    print(test.__str__())
