import os
import json
from user import User
from channel import Channel

class DataLayer:
    """
    Classe destinada à leitura e escrita no arquivo destinado para guardar as informações essencias dos usuários
    """
    
    def __init__(self, usersFile, channelsFile):
        self._usersFilePath      = os.path.join("../", "data", usersFile)
        self._channelsFilesPath  = os.path.join("../", "data", channelsFile)
    
    def readUsers(self):
        """
            Método para ler do arquivo os dados dos usuários
            :return retorna um dicionário onde cada elemento é um objeto User com os dados do usuário
        """  
        try:
            f = open(self._usersFilePath, "r", encoding='utf-8')

            content = json.load(f)
            new_content = {}
            for key, value in content.items():
                new_content[key] = User(value['userName'],value['password'], value['ownChannels'],value['subscribedChannels'])

            f.close()
            
        except Exception as e:
            #print(e)
            new_content = None

        return new_content
        
    def writeUsers(self, users):
        """
            Método para gravar no arquivo as informações dos usuários 
            :param users: um dicionário onde cada elemento é um objeto User
            :return retorna "True" caso as informações dos usuários forem salvas com sucesso. Do contrário, retorna "False" 
        """  
        
        try:
            f = open(self._usersFilePath, "w")

            new_users = {}
            for key, value in users.items():
                new_users[key] = json.loads(value.__str__())

            content = json.dump(new_users, f)

            f.close()

            result = True

        except Exception as e:
            #print(e)
            result = False

        return result

    def readChannels(self):
        """
            Método responsável por ler os canais do arquivo json.
            :return retorna um dicionário onde cada elemento é um objeto Channel com os dados do canal.
        """
        try:
            f = open(self._channelsFilesPath, "r", encoding='utf-8')

            content = json.load(f)
            newContent = {}
            for key, value in content.items():
                newContent[key] = Channel(value['channelName'], value['owner'], value['subscribedUsers'], value['publishedMessages'])

            f.close()
            
        except Exception as e:
            #print(e)
            newContent = None

        return newContent

    def writeChannels(self, channels):
        """
            Método para gravar no arquivo as informações dos canais 
            :param channels: dicionário onde cada elemento é um objeto do tipo Channel com os dados do canal 
            :return retorna True caso os dados tenham sido gravado com sucesso, False caso contrário
        """  
        try:
            f = open(self._channelsFilesPath, "w")

            newChannels = {}
            for key, value in channels.items():
                newChannels[key] = json.loads(value.__str__())
            
            content = json.dump(newChannels, f)

            f.close()

            result = True

        except Exception as e:
            #print(e)
            result = False

        return result

if __name__ == '__main__':
    pass
    # teste = DataLayer('userDatabase.json', 'channelDatabase.json')
    
    # result_users = teste.readUsers()
    # print(result_users)
    # result_users["banana"] = User("banana", "123", [], ["falatu", "banana_clan"])
    # print(teste.writeUsers(result_users))

    # result_channels = teste.readChannels()
    # print(result_channels)
    # result_channels["banana_de_pijamas"] = Channel("banana_de_pijamas", "banana", [], [])
    # print(teste.writeChannels(result_channels))