import socket

HOST = 'localhost' #Endereço do processo passivo
PORTA = 5000       #Porta que o processo passivo estará escutando

sock = socket.socket() #Criação de socket

sock.connect((HOST, PORTA)) #Abertura da conexão com o processo passivo

print("Conectado com o servidor echo.")
print("Caso deseje finalizar a aplicação digite 'FIM'.")
user_msg = str.encode(input("Entre com uma mensagem: "))

while(user_msg != b'FIM'):
    
    sock.send(user_msg) #Envio da mensagem para o processo passivo
    msg = sock.recv(1024) #Recebimento da mensagem enviada pelo processo passivo. OBS: chamada pode ser bloqueante e o argumento indica o tamanho máximo de bytes da msg.

    print(str(msg,  encoding='utf-8'))
    user_msg = str.encode(input("Entre com uma mensagem: "))

sock.close() #Fecha a conexão
