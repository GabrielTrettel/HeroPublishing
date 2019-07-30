#!/usr/bin/python
import sys
sys.path.append('/home/trettel/Documents/projects/BackPlataformaCPE/src/create/')

from dbconnector import DatabaseBridge
from tqdm import tqdm


OUT_DIR = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/publications/"

def get_from_file(file="/var/doutores/queries/pbl/publications_dump.csv"):
    with open(file, 'r') as f:
        for l in f.readlines():
            # print(list(map(lambda x: x.strip('"'), l.strip().split('\t'))))
            yield [x.replace('►', '') for x in l.split("\t")]


def dbcon():
    inputs = dict(
            host     = 'localhost',
            user     = 'FAPESP_GEOPI',
            password = '123',
            database = 'DOUTORES',
            max_changes_to_commit = 1000
            )
    bd = DatabaseBridge(**inputs)

    # This query returns all publications of all authors sorted by author & yr
    query = """SELECT e.cnpq, e.nome, e.nome_cit, a.ano, a.autores, FROM Especialista e
               JOIN Artigo a ON (e.id = a.id_esp)
               WHERE a.ano IS NOT NULL
               ORDER BY e.id, a.ano;"""

    # qry for debug purposes
    # query = """SELECT e.cnpq, e.nome, e.nome_cit, a.ano, a.autores, FROM Especialista e
    #            JOIN Artigo a ON (e.id = a.id_esp)
    #            WHERE (e.cnpq = '4727357182510680')
    #            ORDER BY e.id, a.ano;"""

    data = dict()

    print("Processing data")
    pbar = tqdm(total=5_443_900, ncols=100)

    # for publication in bd.execBigQuery(query, fetch_size=700_000)
    for publication in get_from_file():
        pbar.update(n=1)

        try:
            cnpq, ano, autores = map(str, publication)
        except:
            print(publication)

        if len(autores) < 1: continue

        curr_data = " #@# ".join([ano, autores]) + "\n"

        if cnpq not in data:
            data[cnpq] = list()
        data[cnpq].append(curr_data)


    print("Dumping data")
    for cnpq,text in data.items():
        with open(f"{OUT_DIR}{cnpq}", 'w') as f:
            f.writelines(text)



    pbar.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        OUT_DIR = sys.argv[1] + ('/' if sys.argv[1][-1] != '/' else '')
        # print(OUT_DIR)

    dbcon()
