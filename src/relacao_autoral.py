import pickle
import sys
from datetime import datetime
import time
import os
from filtra_artigos import Publicacao


def requisitos(publ_artigo, publ_evento):
    TEMPO_MAXIMO_ENTRE_PUBLICACOES = 5

    tempo_entre_publicacoes = abs( publ_evento.ano - publ_artigo.ano )

    if( len(publ_artigo.autores) >= 2 and len(publ_evento.autores) >= 2 ):
        if( tempo_entre_publicacoes <= TEMPO_MAXIMO_ENTRE_PUBLICACOES ):
            return True

    return False


def digrafoCorrelacaoAutoral(lista_artigos, lista_eventos):
    texto_grafo = "digraph G {"

    for evento in lista_eventos:
        for artigo in lista_artigos:

            co_autoria = all(autor in artigo.autores  for autor in evento.autores)

            if co_autoria and requisitos(evento, artigo):
                # O grafo é orientado da correlação entre autores que publicaram juntos
                # em evento e posteriormente em revista num tempo maximo TEMPO_MAXIMO_ENTRE_PUBLICACOES
                texto_grafo += "\n\t{} -> {}".format(str(evento.id), str(artigo.id))


    texto_grafo += '\n}'

    return texto_grafo



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

                with open(diretorio_entrada + "/" + 'grafo_coautoriaK-5.txt', 'w') as file:
                    grafo = digrafoCorrelacaoAutoral(lista_artigos, lista_eventos)
                    file.writelines(grafo)


        print('Fim do processamento    : {}\nTempo decorrido         : {:.5} s\n'.format(datetime.now(), time.time()-inicio))

    else:
        print("Argumento diretorio de leitura não encontrado")
