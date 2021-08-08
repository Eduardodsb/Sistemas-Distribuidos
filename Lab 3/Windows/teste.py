import multiprocessing
from time import sleep

def foo(i):
    sleep(2)
    print(f'Sou o {i}')

def main():
    processos = []
    for i in range(0,2):
        processe = multiprocessing.Process(target=foo, args=(i,))
        processos.append(processe)
        processe.start()
        print(f'Eu {i} sai')

    print('ok')
    
    for c in processos: #aguarda todos os processos terminarem
        print('aqui')
        c.join()
        print('foi')

print('teste')
if __name__ == '__main__':
    main()