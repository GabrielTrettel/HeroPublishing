#!/usr/bin/python
import sys
sys.path.append('/home/trettel/Documents/projects/BackPlataformaCPE/src/create/')

from dbconnector import DatabaseBridge
from tqdm import tqdm


OUT_DIR = "/home/trettel/Documents/projects/HeroPublishing/src/max_group_finder/publications/"

def dbcon():
    inputs = dict(
            host     = 'localhost',
            user     = 'FAPESP_GEOPI',
            password =  '123',
            database = 'ESPECIALISTAS',
            max_changes_to_commit = 1000
            )
    bd = DatabaseBridge(**inputs)

    # This query returns all publications of all authors sorted by author & yr
    query = """SELECT e.cnpq, e.nome, e.nome_cit, a.ano, a.autores, a.titulo FROM Especialista e
               JOIN Artigo a ON (e.id = a.id_esp)
               WHERE a.ano IS NOT NULL
               ORDER BY e.id, a.ano;"""

    last_cnpq, curr_data = ("", "")

    pbar = tqdm(total=158_930, ncols=150)

    for publication in bd.execBigQuery(query, fetch_size=700_000):
        pbar.update(n=1)

        cnpq, nome, nomes_cit, ano, autores, titulo = map(str, publication)

        nomes_cit = set(nomes_cit.split(';')) | set([nome])
        autores   = set(autores.split(';')).difference(nomes_cit)
        if len(autores) < 1: continue

        autores = ";".join(autores)
        if cnpq != last_cnpq and curr_data != "":
            last_cnpq = cnpq
            with open(f"{OUT_DIR}{cnpq}", 'w') as f:
                f.writelines(curr_data)
                curr_data = ""
        else:
            titulo = titulo.strip().replace('\n', '').replace(' #@# ','')
            curr_data += " #@# ".join([ano, autores, titulo]) + "\n"

    pbar.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        OUT_DIR = sys.argv[1] + ('/' if sys.argv[1][-1] != '/' else '')
        print(OUT_DIR)

    dbcon()
