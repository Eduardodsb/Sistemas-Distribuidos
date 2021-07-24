import socket

HOST = ''    #'' possibilita acessar qualquer endereco alcancavel da maquina local 
PORTA = 5000 #Porta utilizada pelo processo para ouvir as mensagens

sock = socket.socket() #Cria um socket para a comunicação

sock.bind((HOST, PORTA)) #Vincula a interface e porta para comunicação

sock.listen(5)  #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes

novoSock, endereco = sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou. OBS: A chamada pode ser bloqueante
print ('Conectado com: ', endereco)

while (True) :
    
    msg = novoSock.recv(1024) #Recebe a mensagem do processo ativo
    if (not msg):
        break 
    else:
        print("Mensagem recebida!")
        novoSock.send(msg) #Envia mensagem de resposta para o processo ativo
        print("Mensagem devolvida!") 


novoSock.close() #Fecha o socket
sock.close()  #Fecha o socket principal
