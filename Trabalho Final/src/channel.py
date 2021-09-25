
import threading

class Channel:

    def __init__(self, channelName, ownerUsername, subscribedUsers = [], publishedMessages = []):
        self._owner              = ownerUsername
        self._name               = channelName
        self._subscribedUsers    = subscribedUsers
        self._publishedMessages  = publishedMessages
        self.lock                = threading.Lock()  #Inicializa o lock

    def __str__(self):
        strSubscribedUsers      = '["'+ str("\",\"".join(self._subscribedUsers)) + '"]' if self._subscribedUsers else '[]'
        strPublishedMessages    = '["'+ str("\",\"".join(self._publishedMessages)) + '"]' if self._publishedMessages else '[]'
        return '{' + ' "channelName":"{}", "owner":"{}", "subscribedUsers":{}, "publishedMessages":{}'.format(self._name, self._owner, strSubscribedUsers, strPublishedMessages) +'}' 

    def __repr__(self):
        return self.__str__()

    def getOwner(self):
        return self._owner

    def getName(self):
        return self._name

    def getSubscribedUsers(self):
        return self._subscribedUsers

    def getLastPublishedMessage(self):
        if(len(self._publishedMessages) == 0):
            return None
        else:
            return self._publishedMessages.pop(0)
    
    def publishMessage(self, message):
        self._publishedMessages.append(message)
        
    def subscribeUser(self, userName):
        self._subscribedUsers.append(userName)

    def unsubscribeUser(self, userName):
        self._subscribedUsers.remove(userName)

    def hasPublishedMessage(self):
        return True if self._publishedMessages else False