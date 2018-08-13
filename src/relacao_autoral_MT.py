import pickle
import sys
from datetime import datetime
import time
import os
from filtra_artigos import Publicacao
from collections import deque
import threading

# Versão do "relacao_autoral.py" com funcionamento multithread

def requisitos(publ_artigo, publ_evento):
    TEMPO_MAXIMO_ENTRE_PUBLICACOES = 5

    tempo_entre_publicacoes = abs( publ_evento.ano - publ_artigo.ano )

    if( len(publ_artigo.autores) >= 2 and len(publ_evento.autores) >= 2 ):
        if( tempo_entre_publicacoes <= TEMPO_MAXIMO_ENTRE_PUBLICACOES ):
            return True

    return False

def threader(input):
    eventos = input[1]
    lista_artigos = input[2]
    texto_grafo = ""
    file = input[0]

    while len(eventos) > 0:
        try:
            evento = eventos.pop()

            for artigo in lista_artigos:
                co_autoria = all(autor in artigo.autores  for autor in evento.autores)
                if co_autoria and requisitos(evento, artigo):
                    # O grafo é orientado da correlação entre autores que publicaram juntos
                    # em evento e posteriormente em revista num tempo maximo TEMPO_MAXIMO_ENTRE_PUBLICACOES
                    texto_grafo += "\n\t{} -> {}".format(str(evento.id), str(artigo.id))

        except:
            break

    file.writelines(texto_grafo)

def digrafoCorrelacaoAutoral(arquivo, lista_artigos, lista_eventos, thr):
    fila_eventos = deque(lista_eventos)
    file = open(arquivo, 'w')
    input = [file, fila_eventos, lista_artigos]

    txt = "digraph G {"
    file.writelines(txt)


    threads = []
    for thread in range(thr):
        thread = threading.Thread(target=threader, args=(input,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    txt = "\n}"
    file.writelines(txt)
    file.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        diretorio_entrada = sys.argv[1]

        lista_arquivos = list()
        try:
            lista_arquivos = os.listdir(os.getcwd() + "/" + diretorio_entrada)
        except:
            print("Diretorio não encontrado")

        inicio = time.time()
        print ('\nInicio do processamento : {}'.format(datetime.now()))

        achou_evento = False
        achou_artigo = False
        lista_artigos = []
        lista_eventos = []
        for arquivo in lista_arquivos:

            if arquivo == "Eventos.pkl" and achou_evento == False:
                achou_evento = True
                with open(diretorio_entrada + "/" + arquivo, 'rb') as f1:
                    lista_artigos = pickle.load(f1)

            elif arquivo == "Artigos.pkl" and achou_artigo == False:
                achou_artigo = True
                with open(diretorio_entrada + "/" + arquivo, 'rb') as f2:
                    lista_eventos = pickle.load(f2)

            if achou_artigo and achou_evento:
                achou_evento = False
                achou_artigo = False

                diretorio_saida = diretorio_entrada + "/" + 'grafo_coautoriaMT-K-5.txt'

                thr = 1
                if len(sys.argv) > 2:
                    thr = int(sys.argv[2])

                digrafoCorrelacaoAutoral(diretorio_saida, lista_artigos, lista_eventos, thr)

        print('Fim do processamento    : {}\nTempo decorrido         : {:.5} s\n'.format(datetime.now(), time.time()-inicio))

    else:
        print("Argumento diretório de leitura não encontrado")
