import socket
import select
import multiprocessing
import threading
import json
import sys
import os
import fileDriver
from time import sleep

def treatText(fileData): #Remove pontuações e carcateres que poderiam atrapalhar a comparação das palavras e quebrar as frases em listas de palavras.
    remove = ['.',',',':',';','!','?','"','/','|','(',')','[',']','{','}','<','>'] # Caracteres que serão removidos
    new_fileData = []
    for row in fileData:
        temp = row
        for char in remove:
            temp = temp.replace(char,'') #Substitui os carcateres por vázio
        new_fileData.append(temp)

    result = []
    for index, word in enumerate(new_fileData): #Para cada string da lista a mesma será quebrada em uma lista e somada a lista result
        new_fileData[index] = word.split() #Quebra as frases compostas por mais de uma palavra em uma lista de palavras
        result += [each_string.lower() for each_string in new_fileData[index]] #Transforma a string pra minúsculo e soma a lista result

    return result

def counter(fileData): #Tem como objetivo contar a quantidade de ocorrência de cada palavra do texto.
    counts = dict()
    for i in fileData:
        counts[i.lower()] = counts.get(i.lower(), 0) + 1 #Para cada palavra i, a mesma será passada para minúsculo. Pegará o value no counts e somará 1, caso não exista irá criar uma key com 1 para a palavra nova. 

    return counts

def handler(request):
    file_name = request['file_name']
    word = request['word']

    fileData = fileDriver.readFile(file_name) #Faz a leitura do arquivo
    if(fileData): #Caso o arquivo tenha sido encontrado o mesmo será processado e uma reposta de sucesso retornada 
        fileData = treatText(fileData)
        occurrences = counter(fileData)

        return {'status': 'success', 'data': {'word': word, 'occurrences': occurrences.get(word.lower(),0) }}
    else: #Caso o arquivo não tenha sido encontrado será retornada uma reposta de falha
        return {'status': 'fail', 'data': {'file_name': file_name, 'message': 'file not found'}}

def startServer(HOST, PORTA):
    sock = socket.socket() #Cria um socket para a comunicação
    sock.bind((HOST, PORTA)) #Vincula a interface e porta para comunicação
    sock.listen(5)  #Coloca o processo em modo de espera pela a conexão. O argumento define o limite máximo de conexões pendentes
    sock.setblocking(False) #Configura o sock para o modo não-bloqueante
    sock.settimeout(10) #Define o tempo que ficará esperando por uma conexão antes de seguir em frente
    return sock

def acceptConnection(sock):
    #O accept irá aguardar 10 segundos por uma conexão antes de seguir
    newSock, ipAddress = sock.accept() #Aceita a primeira conexão da fila e retorna um novo socket e o endereço do par ao qual se conectou. OBS: A chamada pode ser bloqueante
    print ('Conectado com: ', ipAddress,'\n')

    return newSock, ipAddress

def handleRequest( clientSock, ipAddress):

    while True:
        request_msg = clientSock.recv(1024) #Recebe a mensagem do processo ativo
        print(f'\nMensagem recebida de {ipAddress}!')
        request = json.loads(request_msg) #Tranformar a mensagem recebida em um dicionário

        if (request['file_name'] == '#' or request['word'] == '#'):
            clientSock.close() #Encerra a conexao com o cliente
            print(f'\nConexão com {ipAddress} fechada!')
            return
        else:     
        
            response = handler(request) #Realiza o processamento da solicitação
            response_msg = json.dumps(response, ensure_ascii=False) #Gera o json para o envio da resposta ao cliente
            clientSock.send(bytes(response_msg,  encoding='utf-8')) #Envia mensagem de resposta para o processo ativo
            print(f'Mensagem devolvida para {ipAddress}!\n')

def read_stdin():
    HOST = 'localhost' #Endereço do processo passivo
    PORTA = 5000       #Porta que o processo passivo estará escutando

    sock_stdin = socket.socket() #Criação de socket
    sock_stdin.connect((HOST, PORTA))
    while True:
        data = sys.stdin.readline().replace('\n','') #Substitui o \n capturado pelo readline por ''
        if data:
            sock_stdin.send(str.encode(data)) #Envia o comando lido do stdin para o próprio servidor via socket
            sleep(1) #Aguarda para dar tempo do fluxo principal atualizar o stop_threads
        global stop_threads
        if stop_threads: #Caso o fluxo principal tenha decidido que a thread deva morre, o stop_threads será definido como True
            sock_stdin.close()
            sys.exit()

stop_threads = False #Utilizado para controlar o tempo de vida da thread

def main():
    HOST = ''    #'' possibilita acessar qualquer endereco alcancavel da maquina local 
    PORTA = 5000 #Porta utilizada pelo processo para ouvir as mensagens

    inputs = []
    connections = {} #Armazena histórico de conexões
    clientProcesses  = [] #Armazena os processos criados.

    print('\nLista de comandos:')
    print('fim: Finalizar o servidor. (OBS: Após esse comando outros comandos não serão aceitos.)')
    print('hist conexoes: Histórico de todas as conexões.')
    print('ativos: Lista as conexões ativas.')
    print('\n=========================================\n\n')

    print('Iniciando o servidor...')
    sock = startServer(HOST, PORTA)
    inputs.append(sock)
    threadStdin = threading.Thread(target=read_stdin).start() #Cria e executa a thread que ficará escutando o stdin e enviando para o servidor
    stdinSock, ipAddress = acceptConnection(sock) #Aceita a conexão do próprio servidor para receber as entradas do stdin
    inputs.append(stdinSock) #Inclui o sock do stdin para ser utilizado no select
    print('Servidor está pronto para receber conexões.')
    
    while (True) :
        #espera por qualquer entrada de interesse
        read, write, exception = select.select(inputs, [], [])
        for trigger in read:
            if trigger == sock: #Caso o trigger seja um nova conexão
                clientSock, ipAddress = acceptConnection(sock)
                connections[clientSock] = ipAddress #Guarda a nova conexão
                processe = multiprocessing.Process(target=handleRequest, args=(clientSock,ipAddress))
                processe.start()
                clientProcesses.append(processe)
            
            elif trigger == stdinSock:
                global stop_threads
                cmd = str(stdinSock.recv(1024), encoding='utf-8').lower()

                if (cmd == 'fim'):
                    stop_threads = True
                    if(len(multiprocessing.active_children()) == 0):
                        print('\nServidor finalizado!')
                    else:
                        print('\nExistem conexões abertas com clientes.')
                        print('Novas conexões não serão aceitas.')
                        print('Aguardando finalização dos clientes existentes...')
                        for c in clientProcesses: #Aguarda todos os processos terminarem
                            c.join()
                        print('Todos os clientes terminaram de usar o servidor.')
                        print('Servidor finalizado!')
                    sock.close()
                    stdinSock.close()
                    sys.exit()
                elif (cmd == 'hist conexoes'):
                    print('\nHistórico de conexões:', list(connections.values()))
                elif (cmd == 'ativos'):
                    print(f'\nExistem {len(multiprocessing.active_children())} clientes ativos.')

if __name__ == '__main__':
    main()