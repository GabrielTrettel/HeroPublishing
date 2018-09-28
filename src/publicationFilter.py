#!/usr/bin/python3
from datetime import datetime
from tqdm import tqdm
from Publication import PublicationList
import time
import xml.etree.ElementTree as ET
import pickle
import os
import sys


def congressFilter(file="0000325690951570.xml"):
    congrr_list = list()
    try:
        root = ET.parse(file).getroot()
    except:
        print(file, "congress can't be parsed")
        return congrr_list

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

        congrr_list.append([authors_list, title, year, id_publ, "Congress", n_cnpq, serial, vehicle])
    return congrr_list

def journalFilter(file="0000325690951570.xml"):
    jour_list = list()
    try:
        root = ET.parse(file).getroot()
    except:
        print(file, "journal can't be parsed")
        return jour_list


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

        jour_list.append([authors_list, title, year, id_publ, "Journal", n_cnpq, serial, vehicle])
    return jour_list

def authorsFilter(input_dir="", output_dir=""):
    begin = time.time()
    print ('Begin processing     : {}\n'.format(datetime.now()))
    authors_list = os.listdir(input_dir)

    pbar = tqdm(total=len(authors_list), ncols=100)

    for author in authors_list:
        if author[0] == ".": continue
        pbar.update(1)
        publications = PublicationList()
        cong_aut_list = congressFilter(input_dir + author)
        jour_aut_list = journalFilter(input_dir + author)
        if len(cong_aut_list)>=1 and len(jour_aut_list)>=1:
            publications.add(congress_list=cong_aut_list, journal_list=jour_aut_list)
            publications.dump(output_dir + author[:-4])


    # journal_publications.write(output_dir + author[:-4] + '-')
    # congress_publications.write(output_dir + author[:-4] + '-')
    pbar.close()
    print('\nEnd of processing    : {}\nElapsed time         : {:.5} s\n'.format(datetime.now(), time.time()-begin))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_dir  = sys.argv[1] + "/"
        output_dir = sys.argv[1] + "-output/"

        try:
            os.mkdir(output_dir)
            print("Creating {}\n".format(output_dir))
        except:
            print("Warning, some files may be overwritten")
            print("Using directory already created: {} \n".format(os.getcwd() + "/" + output_dir ))

        authorsFilter(input_dir, output_dir)

    else:
        print("Invalid arguments\n")
