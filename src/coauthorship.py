#!/usr/bin/python3
import pickle
import sys
from datetime import datetime
from Publication import PublicationList
import time
import os
from tqdm import tqdm
from graph import Graph

def authors_matching(journal_publ, congress_publ):
    return sum([1 for journal_autor in journal_publ.get('authors') if journal_autor in congress_publ.get('authors')])

def requirements(publ1, publ2):
    MAXIMUM_TIME_BETWEEN_PUBLICATIONS = 5
    minimum_coauthorship = 2
    time_between_publications = abs( int(publ2.get('year')) - int(publ1.get('year')))
    coauthorship = authors_matching(publ1, publ2)


    if publ1 == publ2: return False
    if coauthorship > minimum_coauthorship and time_between_publications <= MAXIMUM_TIME_BETWEEN_PUBLICATIONS:
        return True

    return False


def coauthorshipGraph(file, publications_dict):
    edges = {'weight':'INTEGER'}
    graph = Graph(serial='VARCHAR', custom_edges=edges)

    congress_list = publications_dict['Congress']
    journal_list  = publications_dict['Journal']

    for publication in congress_list.union(journal_list):
        graph.addNode(name=publication.get('id'),
                      label=publication.get('type'),
                      serial=publication.get('serial'))

    for congress in congress_list:
        for journal in journal_list:
            if requirements(congress, journal):
                graph.addLink(node1=congress.get('id'),
                              node2=journal.get('id'),
                              weight=authors_matching(journal, congress),
                              label="journal-congress")

    for congress1 in congress_list:
        for congress2 in congress_list:
            if requirements(congress1, congress2):
                graph.addLink(node1=congress1.get('id'),
                              node2=congress2.get('id'),
                              weight=authors_matching(congress1, congress2),
                              label="congress-congress")

    for journal1 in journal_list:
        for journal2 in journal_list:
            if requirements(journal1, journal2):
                graph.addLink(node1=journal1.get('id'),
                              node2=journal2.get('id'),
                              weight=authors_matching(journal1, journal2),
                              label="journal-journal")

    graph.dump(file)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]

        files_list = list()
        try:
            files_list = os.listdir(os.getcwd() + "/" + input_dir)
        except:
            print("Directory not found")

        inicio = time.time()
        print ('\nBegin processing   : {}'.format(datetime.now()))

        pbar = tqdm(total=len(files_list), ncols=100)
        for file in files_list:
            pbar.update(1)
            if file[-4:] == ".pkl":

                output_dir = input_dir + "/../graphs/" + file[:-4] + 'coauthorship.gdf'
                with open(input_dir + "/" + file, 'rb') as f:
                    publications_dict = pickle.load(f)

                coauthorshipGraph(output_dir, publications_dict)
        pbar.close()

        print('End of processing    : {}\nElapsed time         : {:.5} s\n'.format(datetime.now(), time.time()-inicio))

    else:
        print("Reading directory argument not found")
