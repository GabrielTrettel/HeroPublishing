import pickle
import sys
from datetime import datetime
from Publicacao import PublicationList
import time
import os
from collections import deque
import threading


# Versão do "relacao_autoral.py" com funcionamento multithread

def requisitos(journal, congress):
    MAXIMUM_TIME_BETWEEN_PUBLICATIONS = 5

    time_between_publications = abs( congress.year - journal.year )

    if( len(journal.authors) >= 2 and len(congress.authors) >= 2 ):
        if( time_between_publications <= MAXIMUM_TIME_BETWEEN_PUBLICATIONS ):
            return True

    return False

def threader(input):
    congress_list = input[1]
    journal_list = input[2]
    graph = ""
    file = input[0]

    while len(congress_list) > 0:
        try:
            congress = congress_list.pop()

            for artigo in journal_list:
                co_autoria = all(autor in artigo.authors  for autor in congress.authors)
                if co_autoria and requisitos(congress, artigo):
                    # O grafo é orientado da correlação entre authors que publicaram juntos
                    # em congress e posteriormente em revista num tempo maximo MAXIMUM_TIME_BETWEEN_PUBLICATIONS
                    graph += "\n\t{} -> {}".format(str(congress.id), str(artigo.id))

        except:
            break

    file.writelines(graph)

def coauthorshipDigraph(file, journal_list, congress_list, thr):
    congress_list = deque(congress_list)
    file = open(file, 'w')
    input = [file, fila_congress_list, journal_list]

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
        input_dir = sys.argv[1]

        files_list = list()
        try:
            files_list = os.listdir(os.getcwd() + "/" + input_dir)
        except:
            print("Directory not found")

        inicio = time.time()
        print ('\nBegin processing : {}'.format(datetime.now()))

        found_congress = False
        found_journal = False
        journal_list = []
        congress_list = []
        for file in files_list:
            if file == "Congress.pkl" and found_congress == False:
                found_congress = True
                with open(input_dir + "/" + file, 'rb') as f1:
                    journal_list = pickle.load(f1)

            elif file == "Journal.pkl" and found_journal == False:
                found_journal = True
                with open(input_dir + "/" + file, 'rb') as f2:
                    congress_list = pickle.load(f2)


            if found_journal and found_congress:
                found_congress = False
                found_journal = False

                output_dir = input_dir + "/" + 'co-authorship-digraphK-5.txt'

                thr = 1
                if len(sys.argv) > 2:
                    thr = int(sys.argv[2])

                digrafoCorrelacaoAutoral(output_dir, journal_list, congress_list, thr)

        print('End of processing    : {}\nElapsed time         : {:.5} s\n'.format(datetime.now(), time.time()-inicio))

    else:
        print("Reading directory argument not found")
