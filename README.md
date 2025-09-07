# django_enduromcb
Programa em python/django apura resultado de prova de enduro tipo regularidade, tendo como logica a primeira volta de cada piloto serve como referencia para as proximas voltas, perdendo 3 pontos por volta adiantado e 1 ponto por volta atrasado, sempre referente a primeira volta.
O ganhador eh o piloto que perde menos pontos em uma quantidade de voltas pre-definida.
Apresenta relatorio de resultados  por piloto e geral, infomra o tempo de cada volta em rtelacao a volta referencia (volta 01) e calcula os pontos perdidos,  informa o resultado geral  classificando os participantes por pontos perdidos.

Antes de iniciar a prova, configurar nesta seguencia
1 django admin
2 cadastrar pilotos, opcao de importar com arquivo csv
3 cadastrar numeros de voltas em configuracoes da corrida
4 cadastar pilotos em ordem de largada, opcao de importar com arquivo csv
    caso nao cadastrar ordem de laraga, retorna lista de pilotos cadastrados
