
from constants import LOGIN, LOGOUT, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT, ACTIVE_USERS, ACTIVE_STATUS, INACTIVE_STATUS, SHOW_NOTIFICATIONS, OPEN_CHAT, CLOSE_CHAT, DELETE_MESSAGES, SEND_MESSAGE
from constants import HOME_SCR, CREATE_ACCOUNT_SCR, DELETE_ACCOUNT_SCR, LOGIN_SCR, PRINCIPAL_MENU_SCR, CHAT_SCR
import os

class ClientInterface:

    def __init__(self):
        self.currScreen                 = HOME_SCR  #Define a atual tela que deverá ser apresentada
        self.notifications_queue        = []        #Fila que armazena as notificações
        self.notifications_queue_hist   = []        #Fila que guarda o histórico de notificações
        self.messages_queue             = {}        #Fila de mensagens .Ex: {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.MAX_MSGS_SHOW              = 20        #Número máximo de mensagens trocadas entre os usuários que serão apresentadas na tela 
        self.openChatFriendUser         = ""        #Nome do usuário com quem se conversa
        self.username                   = ""        #Nome do usuário da aplicação em si
        self.notification_cmd_flag      = False     #Flag para ativar ou desativar as notificações
        self.canClear                   = True      #Flag para ativar ou desativar a limpeza da tela

    def homeScreen(self):
        """
            Mostra no terminal a tela de home e lê os comandos digitados pelo usuário.
            :return os comandos digitados pelo usuário.
        """        
        self.currScreen = HOME_SCR
        
        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<========== Seja Bem-vindo ao Bate Papo ERT! ===========>\n')
        print('<======================== HOME ========================>\n')
        print(f'Digite "{LOGIN}" para login.')
        print(f'Digite "{CREATE_ACCOUNT}" para criar seu cadastro.')
        print(f'Digite "{DELETE_ACCOUNT}" para deletar o seu cadastro.')
        print(f'Digite "{EXIT}" para fechar a aplicação.\n')
        print('<=========================================================>\n')

        userInput = input()
        while (userInput not in [LOGIN, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT]):
            print('Comando incorreto. Digite um comando válido.')
            userInput = input()
        
        if(userInput == EXIT):
            print("Ficamos triste por sair, mas esperamos vê-lo em breve.")

        return (userInput, None)

    def authScreen(self):
        """
            Mostra no terminal a tela de autenticação do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """        
        self.currScreen = LOGIN_SCR

        print('<=====Fazendo o Login=====>')

        userName     = input('Digite o seu nick: ')
        userPassword = input('Digite a sua senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o seu nick: ')
            userPassword = input('Digite a sua senha: ')

        return userName, userPassword

    def createAccountScreen(self):
        """
            Mostra no terminal a tela de criação da conta do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """         
        self.currScreen = CREATE_ACCOUNT_SCR

        print('<=====Criando Seu Perfil=====>\n')
        
        userName     = input('Digite um nick: ')
        userPassword = input('Digite uma senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite um nick: ')
            userPassword = input('Digite uma senha: ')

        return userName, userPassword

    def deleteAccountScreen(self):
        """
            Mostra no terminal a tela de deleção das credenciais do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """         
        self.currScreen = DELETE_ACCOUNT_SCR

        print('<=====Deletando o Perfil=====>')
        
        userName     = input('Digite o seu nick: ')
        userPassword = input('Digite a sua senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o seu nick: ')
            userPassword = input('Digite a sua senha: ')

        return userName, userPassword

    def readPrincipalMenuScreen(self):
        """
            Lê os comandos digitados pelo usuário na tela de menu principal.
            :return os comandos digitados pelo usuário.
        """         
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
        """
            Mostra no terminal a tela de menu principal. Caso o usuário digite o comando para mostrar as notificações, este método também é responsável por mostrá-las.
        """     
        
        if(self.canClear):
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

        print('<==================== MENU PRINCIPAL ====================>\n')
        print(f'Logado como "{self.username}"')
        print(f'Digite "{ACTIVE_USERS}" para visualizar usuários ativos.')
        print(f'Digite "{ACTIVE_STATUS}" para tornar seu status ativo.')
        print(f'Digite "{INACTIVE_STATUS}" para tornar seu status inativo.')
        print(f'Digite "chat: nome_login" para abrir o chat de conversa com o usuário "nome_login". Por exemplo: {OPEN_CHAT}fabio_Junior19')
        print(f'Digite "{SHOW_NOTIFICATIONS}" mostrar as 5 últimas notificações.')
        print(f'Digite "{LOGOUT}" para se deslogar da sua conta.\n')
        print('<=========================================================>\n')        

    def printChatScreen(self):
        """
            Mostra no terminal a tela de chat com os prints das mensagens digitadas entre os usuários.
        """     
        
        if(self.canClear):
            clear = lambda: os.system('clear')
            clear()
        self.currScreen = CHAT_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])

        print('<========= CHAT COM: '+ str(self.openChatFriendUser) + ' =========>\n')
        print(f'Digite "{CLOSE_CHAT}" para voltar ao menu principal.')
        print(f'Digite "{DELETE_MESSAGES}" para apagar mensagens do chat.')
        print('Digite sua mensagem a ser enviada para este usuário.')
        print('<=========================================================>\n')

        if(self.openChatFriendUser not in self.messages_queue):
            self.messages_queue[self.openChatFriendUser] = []
        messagesToPrint = self.messages_queue[self.openChatFriendUser][-self.MAX_MSGS_SHOW:]
 
        i = 0
        while (i < len(messagesToPrint)):
            if(messagesToPrint):
                print(messagesToPrint[i])
            i += 1

    def readChatScreen(self):
        """
            Lê os comandos e as mensagens a serem enviadas pelo usuário na tela de chat com um par de conversa em específico.
            :return os comandos digitados pelo usuário ou, caso este deseje enviar uma mensagem para seu par, retorna o comando 'SEND_MESSAGE' e a mensagem em si.
        """          
        self.currScreen = CHAT_SCR

        userInput = input()
        if(userInput not in [CLOSE_CHAT, DELETE_MESSAGES]):
            return (SEND_MESSAGE, userInput)
        return (userInput, None)
            
    def handlerResponse(self, response):
        """
            Responsável por tratar as respostas vindas do back e ajustar a interface caso necessário
            :param response: Contém a resposta do back. Podendo ser uam resposta vinda do servidor
        """         
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
                if(response['data']['message'] == 'Você já está logado em outra sessão'):
                    self.notification(HOME_SCR, "Você já está logado em outra sessão. Caso não seja você, entre em contato com o admin do servidor.")
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
        """
            Redireciona de fato para a próxima tela a ser mostrada, informação já contida na variável currScreen.
        """         
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
            userInput = self.readChatScreen()
        else:
            userInput = self.homeScreen()

        return userInput

    def setNextScreen(self, screen):
        """
            Responsável por definir o atributo currScreen com a nova tela que será apresentada
            :param screen: nome da tela que será apresentada
        """       
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
        """
            Adiciona as notificações na fila das notificações e as guarda o histórico de notificações caso o parâmetro "add" seja "True".
            Também é responsável por chamar o método que irá setar qual é a próxima tela.
            :param screen: tela a ser redirecionada
            :param message: mensagem a ser notificada na tela
            :param add: indica se a mensagem deve ser guardada na variável de histórico de notificações ou não
        """  
        if(self.canClear):
            clear = lambda: os.system('clear')
            clear()
        
        self.notifications_queue.append(">>>> " + message + "\n")
        if(add):
            self.notifications_queue_hist.append(">>>> " + message + "\n")

        self.setNextScreen(screen)

    def refreshNotification(self, screen, message, add = True):
        """
            Responsável por atualizar a tela enviada através do parâmetro "screen" com o conteúdo do parâmetro "message".
            :param screen: tela a ser atualizada
            :param message: mensagem a ser notificada na tela
            :param add: indica se a mensagem deve ser guardada na variável de histórico de notificações ou não
        """ 
        if(self.canClear):
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