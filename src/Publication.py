#!/usr/bin/python3

import pickle

class Publication:
    def __init__(self, authors=set(), title="", year="0", id="0", type="", cnpq="", serial="", location=""):
        self.attrs = {
                'authors':set(authors),
                'title':str(title),
                'year':str(year)         if len(str(year))>=1 else '0',
                'type':str(type)         if len(str(type))>=1 else '0',
                'id':str(id)             if len(str(id))>=1   else '0',
                'cnpq':str(cnpq),
                'serial':str(serial),
                'location':str(location)
                }

    def get(self, attr):
        return self.attrs[attr]

class PublicationList:
    def __init__(self):
        self.publications_list = dict()
        self.publications_list['Congress'] = set()
        self.publications_list['Journal'] = set()

    def add(self, congress_list=[], journal_list=[]):
        for publication in congress_list:
            self.publications_list['Congress'].add( Publication(*publication) )

        for publication in journal_list:
            self.publications_list['Journal'].add( Publication(*publication) )


    def dump(self, out_folder=""):
        # picke dump stuff
        file = out_folder + ".pkl"
        with open(file, 'wb') as ar:
            pickle.dump(self.publications_list, ar)


    def write(self, out_folder=""):
        # write informations in a file

        for type,publ_list in publications_list.items():
            file = out_folder + type
            with open(file+".csv", 'w') as file:
                for publication in publ_list:
                    line =  "\t".join([publication.get('cnpq'),publication.get('serial'),
                                       publication.get('title'),publication.get('year')])

                    line += "\t" + ",".join(publication.get('authors'))
                    line += '\t' + publication.get('vehicle') + '\n'

                    file.writelines(line)
