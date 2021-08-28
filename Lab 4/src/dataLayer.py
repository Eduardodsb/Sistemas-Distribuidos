import os
import json
from user import User

class DataLayer:
    """
        Classe destinada à leitura e escrita no arquivo destinado para guardar as informações essencias dos usuários
    """
         
    def __init__(self, filename):
        self._filename = filename
        self._path     = os.path.join("../", "data", filename)
    
    def readUsers(self):
        try:
            f = open(self._path, "r")

            content = json.load(f)
            new_content = {}
            for key, value in content.items():
                new_content[key] = User(value['userName'],value['password'],int(value['status']),value['ip'],int(value['port']))
            
            f.close()
            
        except Exception as e:
            print(e)
            new_content = None

        return new_content
        
    def writeUsers(self, users):
        try:
            f = open(self._path, "w")

            new_users = {}
            for key, value in users.items():
                new_users[key] = json.loads(value.__str__(True, True, True, True, True))
            
            content = json.dump(new_users, f)

            f.close()

            result = True

        except Exception as e:
            print(e)
            result = False

        return result

if __name__ == '__main__':

    teste = DataLayer('../data/dataBase.json')
    result = teste.readUsers()
    print(teste.writeUsers(result))