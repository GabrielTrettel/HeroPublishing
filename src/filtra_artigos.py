import threading
from collections import deque
from datetime import datetime
import time
import xml.etree.ElementTree as ET
import pickle
import os
import sys

class Publicacao:
    def __init__(self, autores="", titulo="", ano=0, id=0, tipo="", cnpq=""):
        self.autores = set(autores)
        self.titulo = titulo
        self.ano = int(ano)
        self.tipo_da_publicacao = tipo
        self.id = id
        self.numero_identificador = cnpq


    # def normalizaAtributos(): TODO


def filtraEvento(arquivo="0000325690951570.xml"):
    root = ET.parse(arquivo).getroot()
    lista_eventos = list()

    for evento in root.iter('TRABALHO-EM-EVENTOS'):

        list_autores = list()
        for autores in evento.iter('AUTORES'):
            list_autores.append(autores.get('NOME-COMPLETO-DO-AUTOR'))

        titulo = evento.find('DADOS-BASICOS-DO-TRABALHO').get('TITULO-DO-TRABALHO')
        ano = evento.find('DADOS-BASICOS-DO-TRABALHO').get('ANO-DO-TRABALHO')
        id = evento.get('SEQUENCIA-PRODUCAO')

        publicacao = Publicacao(list_autores, titulo, ano, id,"Evento", root.get('NUMERO-IDENTIFICADOR'))
        lista_eventos.append(publicacao)

    return lista_eventos


def filtraArtigo(arquivo="0000325690951570.xml"):
    root = ET.parse(arquivo).getroot()
    lista_artigos = list()

    for artigo in root.iter('ARTIGO-PUBLICADO'):

        list_autores = list()
        for autores in artigo.iter('AUTORES'):
            list_autores.append(autores.get('NOME-COMPLETO-DO-AUTOR'))

        titulo = artigo.find('DADOS-BASICOS-DO-ARTIGO').get('TITULO-DO-ARTIGO')
        ano = artigo.find('DADOS-BASICOS-DO-ARTIGO').get('ANO-DO-ARTIGO')
        id = artigo.get('SEQUENCIA-PRODUCAO')

        publicacao = Publicacao(list_autores, titulo, ano, id, "Artigo")
        lista_artigos.append(publicacao)

    return lista_artigos


def salvarDados(lista_publicacao, out_folder):

    for publ in lista_publicacao:

        tipo = publ[0].tipo_da_publicacao
        arquivo = out_folder + tipo + "s"

        with open(arquivo+".pkl", 'wb') as ar:
            pickle.dump(publ, ar)

        with open(arquivo+".csv", 'w') as file:

            for publicacao in publ:
                line = ""
                line += publicacao.numero_identificador + '\t'
                line += publicacao.id + '\t'
                line += publicacao.titulo + '\t'
                line += str(publicacao.ano) + '\t'


                for autor in publicacao.autores:
                    line += autor + ','

                line = line[:-1] # Retira a ultima virgula que sobra do laço dos autores

                line += '\n'
                file.writelines(line)


def filtraAutores(diretorio_entrada="", diretorio_saida="", thr_qtd=1):

# -----------------------------------------------------
    def threader(d):
        while(len(d) > 0):
            try:
                arquivo = str(d.pop())
                lista_eventos.extend(filtraEvento(diretorio_entrada + arquivo))
                lista_artigos.extend(filtraArtigo(diretorio_entrada + arquivo))
            except:
                break
# -----------------------------------------------------

    print ('Inicio do processamento : {}'.format(datetime.now()))
    inicio = time.time()

    lista_eventos = list()
    lista_artigos = list()

    fila_autores = deque(os.listdir(diretorio_entrada))

    threads = []
    for thread in range(thr_qtd):
        thread = threading.Thread(target=threader, args=(fila_autores,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


    salvarDados([lista_eventos, lista_artigos], diretorio_saida)

    print('Fim do processamento    : {}\nTempo decorrido         : {:.5} s\n'.format(datetime.now(), time.time()-inicio))



if __name__ == "__main__":
    if sys.argv[1] == "--help":
        print("\nPrograma criado para separar publicações de eventos e periódicos.")
        print("O primeiro argumento precisa ser o caminho até o diretório contendo")
        print("os arquivos xml utilizados de entrada, e o segundo a quantidade de")
        print("threads desejada, se não informado, 1 por padrão\n")

    elif len(sys.argv) > 1:
        diretorio_entrada = sys.argv[1] + "/"
        diretorio_saida   = sys.argv[1] + "-output/"

        try:
            os.mkdir(diretorio_saida)
            print("\nCriando {}\n".format(diretorio_saida))

        except:
            print("\nAtenção, alguns arquivos podem ser sobrescritos")
            print("Utilizando diretório já criado : {} \n".format(os.getcwd() + "/" + diretorio_saida ))


        thr = 1
        if len(sys.argv) > 2:
            thr = int(sys.argv[2])

        filtraAutores(diretorio_entrada, diretorio_saida, thr)

    else:
        print("Argumentos inválidos \n --help para instruções\n")
