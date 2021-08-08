def readFile(path):
    try:
        file = open(path, 'r', encoding='utf-8') # Abre o arquivo
        fileData = file.read().splitlines() # Ler linhas do arquivo
        file.close() # Fecha o arquivo
        return fileData # Retorna uma lista com as linhas do arquivo
    except FileNotFoundError:
        print('Arquivo não encontrado.')
        return False # Retorna Falso caso o arquivo não seja encontrado