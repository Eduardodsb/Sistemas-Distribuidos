import socket
import json
import sys

def printResult(response): #Responsável por tratar e imprimir o resultado para o usuário
    if(response['status'] == 'success'): #Para o caso de resposta de sucesso.
        word = response['data']['word']
        occurrences = response['data']['occurrences']
        print(f'\nO resultado da busca pela palavra "{word}", foi de {occurrences} ocorrências!\n' )
    elif(response['status'] == 'fail' and response['data']['message'] == 'file not found'): #Para o caso de resposta de falha.
        file_name = response['data']['file_name']
        print(f'\nNão foi possível localizar o arquivo "{file_name}"!\n')
    else: #Para o caso de resposta inesperada.
        print('\nUm erro inesperado ocorreu!\n')

def main():

    HOST = 'localhost' #Endereço do processo passivo
    PORTA = 5000       #Porta que o processo passivo estará escutando

    sock = socket.socket() #Criação de socket
   
    print("\n\n=====Contador de Palavras=====")
    
    try:
        sock.connect((HOST, PORTA)) #Abertura da conexão com o processo passivo
        print("Conexão com o servidor estabelecida.\n")
    except Exception:
        print("Não foi ppossível se conectar ao servidor.")
        print("Encerrando.")
        sys.exit(1)

    print("- A aplicação não faz distinção de maiúsculo e minúsculo na palavra de busca.")
    print("- Caso deseje finalizar a aplicação digite '#' no lugar do nome do arquivo ou da palavra que deseje buscar.\n")
    
    file_name = input("Entre com o path/nome_do_arquivo.txt: ")
    word = input("Entre com a palavra que deseje buscar: ")

    request = {'file_name': file_name, 'word': word}
    request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor

    while(True):
        
        sock.send(bytes(request_msg,  encoding='utf-8')) #Envio da mensagem para o processo passivo
        
        if(file_name == '#' or word == '#'):
            break

        response_msg = sock.recv(1024) #Recebimento da mensagem enviada pelo processo passivo. OBS: chamada pode ser bloqueante e o argumento indica o tamanho máximo de bytes da msg.
        response = json.loads(response_msg) #Tranformar a mensagem recebida em um dicionário.

        printResult(response) #Chama a função responsável por editar e tratar a resposta do servidor.

        file_name = input("Entre com o path/nome_do_arquivo.txt: ")
        word = input("Entre com a palavra que deseje buscar: ")
        
        request = {'file_name': file_name, 'word': word}
        request_msg = json.dumps(request, ensure_ascii=False) #Gera o json para o envio da requisição ao servidor

    sock.close() #Fecha a conexão

main()