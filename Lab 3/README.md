# Laboratório 3

Nesse laboratório 3 expandimos a implementação realizada no laboratório 2 que era constituído por um servidor interativo
para um servidor concorrente realizando o uso de multithreads e/ou multiprocessos.

### Cliente

No cliente não houve alterações em relação ao que foi realizado no lab 2.
O mesmo continua se comunicando com o servidor por meio de jsons.

### Servidor

Quanto ao servidor o mesmo passou a atender de forma concorrente mais de um cliente
e para isso foi utilizado multiprocessos. Além disso, o servidor também passou a permitir a leitura do que é digitado no terminal.
Os comandos disponíveis são:

<b>fim:</b> Finaliza o servidor. (OBS: Após esse comando outros comandos não serão aceitos.).<br>
<b>hist conexoes:</b> Histórico de todas as conexões que foram realizadas com servidor.<br>
<b>ativos:</b> Lista as conexões ativas.<br>

