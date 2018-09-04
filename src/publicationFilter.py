import threading
from collections import deque
from datetime import datetime
import time
import xml.etree.ElementTree as ET
import pickle
import os
import sys
from Publication import PublicationList


def congressFilter(congress_publications, file="0000325690951570.xml"):
    root = ET.parse(file).getroot()

    for congress in root.iter('TRABALHO-EM-EVENTOS'):
        authors_list = list()
        for authors in congress.iter('AUTORES'):
            authors_list.append(authors.get('NOME-COMPLETO-DO-AUTOR'))

        n_cnpq  = root.get('NUMERO-IDENTIFICADOR')
        id_publ = congress.get('SEQUENCIA-PRODUCAO')
        title   = congress.find('DADOS-BASICOS-DO-TRABALHO').get('TITULO-DO-TRABALHO')
        year    = congress.find('DADOS-BASICOS-DO-TRABALHO').get('ANO-DO-TRABALHO')
        vehicle = congress.find('DETALHAMENTO-DO-TRABALHO').get('TITULO-DOS-ANAIS-OU-PROCEEDINGS')
        serial  = congress.find('DETALHAMENTO-DO-TRABALHO').get('ISBN')

        congress_publications.add(authors_list, title, int(year), int(id_publ), "Congress", n_cnpq, serial, vehicle)

    return congress_publications


def journalFilter(journal_publications, file="0000325690951570.xml"):
    root = ET.parse(file).getroot()

    for journal in root.iter('ARTIGO-PUBLICADO'):
        authors_list = list()
        for autores in journal.iter('AUTORES'):
            authors_list.append(autores.get('NOME-COMPLETO-DO-AUTOR'))

        n_cnpq  = root.get('NUMERO-IDENTIFICADOR')
        id_publ = journal.get('SEQUENCIA-PRODUCAO')
        title   = journal.find('DADOS-BASICOS-DO-ARTIGO').get('TITULO-DO-ARTIGO')
        year    = journal.find('DADOS-BASICOS-DO-ARTIGO').get('ANO-DO-ARTIGO')
        vehicle = journal.find("DETALHAMENTO-DO-ARTIGO").get("TITULO-DO-PERIODICO-OU-REVISTA")
        serial  = journal.find("DETALHAMENTO-DO-ARTIGO").get("ISSN")

        journal_publications.add(authors_list, title, int(year), int(id_publ), "Journal", n_cnpq, serial, vehicle)

    return journal_publications


def authorsFilter(input_dir="", output_dir="", thr_qtd=1):
    congress_publications = PublicationList("Congress")
    journal_publications  = PublicationList("Journal")

#=========================threader=========================#
    def threader(queue):
        while(len(queue) > 0):
            try:
                file = str(queue.pop())
                journalFilter(journal_publications, input_dir + file)
                congressFilter(congress_publications, input_dir + file)
            except:
                break
#=========================threader=========================#

    print ('Begin processing     : {}'.format(datetime.now()))
    begin = time.time()

    authors_queue = deque(os.listdir(input_dir))

    threads = []
    for thread in range(thr_qtd):
        thread = threading.Thread(target=threader, args=(authors_queue,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


    congress_publications.write(output_dir)
    congress_publications.dump(output_dir)

    journal_publications.write(output_dir)
    journal_publications.dump(output_dir)

    print('End of processing    : {}\nElapsed time         : {:.5} s\n'.format(datetime.now(), time.time()-begin))



if __name__ == "__main__":

    if len(sys.argv) > 1:
        input_dir = sys.argv[1] + "/"
        output_dir   = sys.argv[1] + "-output/"

        try:
            os.mkdir(output_dir)
            print("\nCreating {}\n".format(output_dir))

        except:
            print("\nWarning, some files may be overwritten")
            print("Using directory already created: {} \n".format(os.getcwd() + "/" + output_dir ))


        thr = 1
        if len(sys.argv) > 2:
            thr = int(sys.argv[2])

        authorsFilter(input_dir, output_dir, thr)

    else:
        print("Invalid arguments\n")
