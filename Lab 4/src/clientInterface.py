
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS, SHOW_NOTIFICATIONS, OPEN_CHAT, CLOSE_CHAT, DELETE_MESSAGES, SEND_MESSAGE
from constants import HOME_SCR, CREATE_ACCOUNT_SCR, DELETE_ACCOUNT_SCR, LOGIN_SCR, PRINCIPAL_MENU_SCR, CHAT_SCR
import os

class ClientInterface:

    def __init__(self):
        self.currScreen                 = HOME_SCR
        self.notifications_queue        = []
        self.notifications_queue_hist   = []
        self.messages_queue             = {} # {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.MAX_MSGS_SHOW              = 5
        self.openChatFriendUser         = ""
        self.username                   = ""
        self.notification_cmd_flag      = False

    def homeScreen(self):
        self.currScreen = HOME_SCR
        
        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<=====Seja Bem-vindo ao Bate Papo ERT=====>\n')
        print(f'Digite "{LOGIN}" para login.')
        print(f'Digite "{CREATE_ACCOUNT}" para criar seu cadastro.')
        print(f'Digite "{DELETE_ACCOUNT}" para deletar o seu cadastro.')
        print(f'Digite "{EXIT}" para fechar a aplicação.\n')

        userInput = input()
        while (userInput not in [LOGIN, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT]):
            print('Comando incorreto. Digite um comando válido.')
            userInput = input()
        
        if(userInput == EXIT):
            print("Ficamos triste por sair, mas esperamos vê-lo em breve.")

        return (userInput, None)

    def authScreen(self):
        self.currScreen = LOGIN_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<=====Fazendo o Login=====>')

        userName     = input('Digite o seu nick: ')
        userPassword = input('Digite a sua senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o seu nick: ')
            userPassword = input('Digite a sua senha: ')

        return userName, userPassword

    def createAccountScreen(self):
        self.currScreen = CREATE_ACCOUNT_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<=====Criando Seu Perfil=====>\n')
        
        userName     = input('Digite um nick: ')
        userPassword = input('Digite uma senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite um nick: ')
            userPassword = input('Digite uma senha: ')

        return userName, userPassword

    def deleteAccountScreen(self):
        self.currScreen = DELETE_ACCOUNT_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<=====Deletando o Perfil=====>')
        
        userName     = input('Digite o seu nick: ')
        userPassword = input('Digite a sua senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o seu nick: ')
            userPassword = input('Digite a sua senha: ')

        return userName, userPassword

    def readPrincipalMenuScreen(self):
        self.currScreen = PRINCIPAL_MENU_SCR

        userInput = input()
        while (userInput not in [LOGOUT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS, SHOW_NOTIFICATIONS]) and (userInput[:5] != OPEN_CHAT):
            print('Comando incorreto. Digite um comando válido.')
            userInput = input()
 
        if(userInput == SHOW_NOTIFICATIONS):
            self.notification_cmd_flag = True
        else:
            self.notification_cmd_flag = False

        return (userInput, None)

    def printPrincipalMenuScreen(self):
        clear = lambda: os.system('clear')
        clear()
        self.currScreen = PRINCIPAL_MENU_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        if(self.notification_cmd_flag):
            msg = "-------\nNOTIFICAÇÕES\n"
            tam_noti_hist = len(self.notifications_queue_hist)

            if(tam_noti_hist == 0):
                msg += "Não há notificações\n"
            else:
                for n in self.notifications_queue_hist[ ( -5 if tam_noti_hist >= 5 else (-1)*tam_noti_hist ) :]:
                    msg += n 
            msg += "-------\n"

            print(msg)

        print('<=====Menu Principal=====>\n')
        print(f'Digite "{ACTIVE_USERS}" para visualizar usuários ativos.')
        print(f'Digite "{ACTIVE_STATUS}" para tornar seu status ativo.')
        print(f'Digite "{INACTIVE_STATUS}" para tornar seu status inativo.')
        print(f'Digite "chat: nome_login" para abrir o chat de conversa com o usuário "nome_login". Por exemplo: {OPEN_CHAT}fabio_Junior19')
        print(f'Digite "{SHOW_NOTIFICATIONS}" mostrar as 5 últimas notificações.')
        print(f'Digite "{LOGOUT}" para se deslogar da sua conta.\n')

    def printChatScreen(self):
        clear = lambda: os.system('clear')
        clear()
        self.currScreen = CHAT_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<===== CHAT: '+ str(self.openChatFriendUser) + ' =====>\n')
        print(f'Digite "{CLOSE_CHAT}" para voltar ao menu principal.')
        print(f'Digite "{DELETE_MESSAGES}" para apagar mensagens do chat.')
        print('Digite sua mensagem a ser enviada para este usuário.')
        print('<==============>\n')

        if(self.openChatFriendUser not in self.messages_queue):
            self.messages_queue[self.openChatFriendUser] = []
        messagesToPrint = self.messages_queue[self.openChatFriendUser][-self.MAX_MSGS_SHOW:]
 
        i = 0
        while (i < len(messagesToPrint)):
            if(messagesToPrint):
                print(messagesToPrint[i])
            i += 1

    def readChatScreen(self):
        self.currScreen = CHAT_SCR

        userInput = input()
        if(userInput not in [CLOSE_CHAT, DELETE_MESSAGES]):
            return (SEND_MESSAGE, userInput)
        return (userInput, None)
            
    def handlerResponse(self, response):
        if(response['method'] == 'createAccount'):
            if(response['status'] == 'success'):
                self.notification(CREATE_ACCOUNT_SCR, "Conta criada com sucesso.")
            else:
                self.notification(CREATE_ACCOUNT_SCR, "Houve um problema. Não foi possível criar a conta. Tente novamente.")
        
        elif(response['method'] == 'deleteAccount'):
            if(response['status'] == 'success'):
                self.notification(DELETE_ACCOUNT_SCR, "Conta deletada com sucesso.")
            else:
                self.notification(DELETE_ACCOUNT_SCR, "Houve um problema. Não foi possível deletar a conta. Tente novamente.")

        elif(response['method'] == 'authAccount'):
            if(response['status'] == 'success'):
                self.notification(LOGIN_SCR, "Logado com sucesso.")
            else:
                self.notification(HOME_SCR, "Houve um problema. Não foi possível logar na conta. Tente novamente.")

        elif(response['method'] == 'getUsers'):
            if(response['status'] == 'success'):
                msg = "USUÁRIOS ATIVOS\n"
                for user_ in response['data']:
                    if(user_['status'] == '1'):
                        msg += "    " + user_['userName'] + "\n"
                msg = msg.rstrip()
                self.notification(PRINCIPAL_MENU_SCR, msg, False)
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível listar usuários ativos. Tente novamente.")

        elif(response['method'] == 'logout'):
            if(response['status'] == 'success'):
                self.notification(HOME_SCR, response['data']['message'])
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível deslogar da conta. Tente novamente.")
 
        elif(response['method'] == 'setMyStatus'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, 'Seu status foi redefinido.')
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível alterar o seu status. Tente novamente.")

        elif(response['method'] == 'openChat'):
            if(response['status'] == 'success'):
                self.notification(CHAT_SCR, "Chat aberto com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Não foi possível abrir o chat. Tente novamente.")

        elif(response['method'] == 'closeChat'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Chat fechado com sucesso.")
            else:
                self.notification(CHAT_SCR, "Não foi possível fechar o chat. Tente novamente.")

        elif(response['method'] == 'deleteMessages'):
            if(response['status'] == 'success'):
                self.notification(CHAT_SCR, "Chat apagado com sucesso.")
            else:
                self.notification(CHAT_SCR, "Não foi possível apagar o chat. Tente novamente.")

    def redirectScreen(self):
        if(self.currScreen == HOME_SCR):
            userInput = self.homeScreen()

        elif(self.currScreen == CREATE_ACCOUNT_SCR):
            userInput = self.createAccountScreen()

        elif(self.currScreen == DELETE_ACCOUNT_SCR):
            userInput = self.deleteAccountScreen()

        elif(self.currScreen == LOGIN_SCR):
            userInput = self.authScreen()
        
        elif(self.currScreen == PRINCIPAL_MENU_SCR):
            self.printPrincipalMenuScreen()
            userInput = self.readPrincipalMenuScreen()

        elif(self.currScreen == CHAT_SCR):
            self.printChatScreen()
            #print('querida cheguei')
            userInput = self.readChatScreen()
            #print('querida cheguei 1')

        else:
            userInput = self.homeScreen()

        return userInput

    def setNextScreen(self, screen):
        if(screen == HOME_SCR):
            self.currScreen = HOME_SCR

        elif(screen == CREATE_ACCOUNT_SCR):
            self.currScreen = HOME_SCR

        elif(screen == DELETE_ACCOUNT_SCR):
            self.currScreen = HOME_SCR

        elif(screen == LOGIN_SCR):
            self.currScreen = PRINCIPAL_MENU_SCR

        elif(screen == PRINCIPAL_MENU_SCR):
            self.currScreen = PRINCIPAL_MENU_SCR

        elif(screen == CHAT_SCR):
            self.currScreen = CHAT_SCR

        else:
            self.currScreen = HOME_SCR

    def notification(self, screen, message, add = True):
        clear = lambda: os.system('clear')
        clear()
        
        self.notifications_queue.append(">>>> " + message + "\n")
        if(add):
            self.notifications_queue_hist.append(">>>> " + message + "\n")

        self.setNextScreen(screen)

    def refreshNotification(self, screen, message, add = True):
        clear = lambda: os.system('clear')
        clear()

        self.notifications_queue.append(">>>> " + message + "\n")
        if(add):
            self.notifications_queue_hist.append(">>>> " + message + "\n")

        if(screen == PRINCIPAL_MENU_SCR):
            self.printPrincipalMenuScreen()
        elif(screen == CHAT_SCR):
            self.printChatScreen()
        
        
            
if __name__ == '__main__':
        
    teste = ClientInterface()
    teste.home()