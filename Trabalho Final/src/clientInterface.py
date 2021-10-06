
from constants import LOGOUT, CREATE_CHANNEL, SUBSCRIBE_CHANNEL, UNSUBSCRIBE_CHANNEL, SHOW_MY_SUBS, PUBLISH_CHANNEL, SHOW_MY_CHANNELS, SHOW_ALL_CHANNELS
from constants import LOGIN, CREATE_ACCOUNT, DELETE_ACCOUNT, EXIT 
from constants import HOME_SCR, CREATE_ACCOUNT_SCR, DELETE_ACCOUNT_SCR, LOGIN_SCR, PRINCIPAL_MENU_SCR
import os

class ClientInterface:

    def __init__(self):
        self.currScreen                 = HOME_SCR  #Define a atual tela que deverá ser apresentada
        self.messages_queue             = []        #Fila de mensagens .Ex: {'fabio_Junior19': ["você:ola", "fabio_Junior19:ola", "fabio_Junior19:tudobom?"]}
        self.responsesToPrint           = []        #Fila de repostas do servidor que devem ser printadas no console
        self.MAX_MSGS_SHOW              = 20        #Número máximo de mensagens trocadas entre os usuários que serão apresentadas na tela 
        self.username                   = ""        #Nome do usuário da aplicação em si
        self.notifications_queue        = []        #Fila que armazena as notificações
        self.notifications_queue_hist   = []        #Fila que guarda o histórico de notificações
        self.canClear                   = True      #Flag para ativar ou desativar a limpeza da tela

    def homeScreen(self):
        """
            Mostra no terminal a tela de home e lê os comandos digitados pelo usuário.
            :return os comandos digitados pelo usuário.
        """        
        self.currScreen = HOME_SCR

        if(self.notifications_queue):
            print(self.notifications_queue[len(self.notifications_queue) - 1])
        
        print('<========== Seja Bem-vindo ao Sistema de Canais ERT! ===========>\n')
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
            print("Serviço finalizado com sucesso.")

        return (userInput, None)

    def authScreen(self):
        """
            Mostra no terminal a tela de autenticação do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """        
        self.currScreen = LOGIN_SCR

        print('<=====Fazendo o Login=====>')

        userName     = input('Digite o usuário: ')
        userPassword = input('Digite a senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o usuário: ')
            userPassword = input('Digite a senha: ')

        return userName, userPassword

    def createAccountScreen(self):
        """
            Mostra no terminal a tela de criação da conta do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """         
        self.currScreen = CREATE_ACCOUNT_SCR

        print('<=====Criando Seu Perfil=====>\n')
        
        userName     = input('Digite o usuário: ')
        userPassword = input('Digite a senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o usuário: ')
            userPassword = input('Digite a senha: ')

        return userName, userPassword

    def deleteAccountScreen(self):
        """
            Mostra no terminal a tela de deleção das credenciais do usuário e lê as entradas digitados pelo usuário.
            :return as entradas digitados pelo usuário.
        """         
        self.currScreen = DELETE_ACCOUNT_SCR

        print('<=====Deletando o Perfil=====>')
        
        userName     = input('Digite o usuário: ')
        userPassword = input('Digite a senha: ')
        while((not userName or userName.isspace()) and (not userPassword or userPassword.isspace())):
            userName     = input('Digite o usuário: ')
            userPassword = input('Digite a senha: ')

        return userName, userPassword

    def readPrincipalMenuScreen(self):
        """
            Lê os comandos digitados pelo usuário na tela de menu principal.
            :return os comandos digitados pelo usuário.
        """         
        self.currScreen = PRINCIPAL_MENU_SCR

        userInput       = input()

        while ((userInput not in [LOGOUT, SHOW_MY_SUBS, SHOW_MY_CHANNELS, SHOW_ALL_CHANNELS]) and
        (CREATE_CHANNEL + ":" not in userInput) and (SUBSCRIBE_CHANNEL + ":" not in userInput) and
        (UNSUBSCRIBE_CHANNEL + ":" not in userInput) and (PUBLISH_CHANNEL + ":" not in userInput or '<' not in userInput)):
            print('Comando incorreto. Digite um comando válido.')
            userInput = input()

        result  = None
        infos   = userInput.split(':')
        
        if(infos[0] in PUBLISH_CHANNEL):
            cmd              = infos[0]
            channelName, msg = infos[1].split('<')
            result           = (cmd, (channelName, msg))
        elif(infos[0] in [CREATE_CHANNEL, SUBSCRIBE_CHANNEL, UNSUBSCRIBE_CHANNEL]):
            cmd              = infos[0]
            channelName      = infos[1]
            result           = (cmd, channelName)
        else:
            cmd              = infos[0]
            result           = (cmd, None)
            
        return result

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

        print('<==================== MENU PRINCIPAL ====================>\n')
        print(f'Logado como "{self.username}"')
        print(f'Digite "{SHOW_ALL_CHANNELS}" para visualizar todos os canais existentes.')
        print(f'Digite "{SHOW_MY_CHANNELS}" para visualizar todos os canais que você é proprietário.')
        print(f'Digite "{SHOW_MY_SUBS}" para visualizar todos os canais em que você está inscrito.')
        print(f'Digite "{CREATE_CHANNEL}:<nome do canal>" para criar um canal.')
        print(f'Digite "{SUBSCRIBE_CHANNEL}:<nome do canal>" para se inscrever em um canal')
        print(f'Digite "{UNSUBSCRIBE_CHANNEL}:<nome do canal>" para se desinscrever em um canal')
        print(f'Digite "{PUBLISH_CHANNEL}:<nome do canal> < <mensagem>" para publicar uma mensagem')

        print(f'Digite "{LOGOUT}" para se deslogar da sua conta.\n')
        print('<=========================================================>\n')      

        if(self.responsesToPrint):
            print('<================Informações==============================>\n')  
            print(self.responsesToPrint[-1])

        messagesToPrint = self.messages_queue[-self.MAX_MSGS_SHOW:]
        if(messagesToPrint):
            print('<================Mensagens dos Canais=====================>\n')
            for msg in messagesToPrint:
                print(msg)
        
    def handlerResponse(self, response):
        """
            Responsável por tratar as respostas vindas do back e ajustar a interface caso necessário
            :param response: Contém a resposta do back. Podendo ser uma resposta vinda do servidor
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

        elif(response['method'] == 'logout'):
            if(response['status'] == 'success'):
                self.notification(HOME_SCR, response['data']['message'])
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível deslogar da conta. Tente novamente.")
 
        elif(response['method'] == 'publishChannel'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Mensagem enviada com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível publicar a mensagem. Tente novamente.")

        elif(response['method'] == 'subscribeChannel'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Inscrição realizada com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível se inscrever no canal. Tente novamente.")

        elif(response['method'] == 'unsubscribeChannel'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Desinscrição realizada com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível se desinscrever do canal. Tente novamente.")

        elif(response['method'] == 'showMySubscriptions'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Subinscrições retornadas sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível visualizar os canais subscritos. Tente novamente.")
        
        elif(response['method'] == 'showMyOwnChannels'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Seus canais foram retornados com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível visualizar os próprios canais criados. Tente novamente.")

        elif(response['method'] == 'showAllChannels'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Todos os canais foram retornados foram retornados com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível visualizar todos os canais existentes. Tente novamente.")

        elif(response['method'] == 'createChannel'):
            if(response['status'] == 'success'):
                self.notification(PRINCIPAL_MENU_SCR, "Canal foi criado com sucesso.")
            else:
                self.notification(PRINCIPAL_MENU_SCR, "Houve um problema. Não foi possível criar o canal. Tente novamente.")
    
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

        else:
            self.currScreen = HOME_SCR

    def notification(self, screen, message, add = True):
        """
            É responsável por chamar o método que irá setar qual é a próxima tela.
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

            
if __name__ == '__main__':
    pass
    #teste = ClientInterface()
    #teste.home()