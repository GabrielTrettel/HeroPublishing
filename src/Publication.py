import pickle

class Publication:
    def __init__(self, authors, title, year, id, type, cnpq, serial, vehicle):
        self.authors = set(authors)
        self.title = title
        self.year = int(year)
        self.type = type
        self.id = id
        self.cnpq = cnpq
        self.serial = serial
        self.vehicle = vehicle

    # def normalizaAtributos(): TODO

class PublicationList:
    def __init__(self, kind):
        self.publications_list = set()
        self.kind = kind


    def add(self, authors, title, year, id, type, cnpq, serial, vehicle):
        publ = Publication(authors, title, year, id, type, cnpq, serial, vehicle)
        self.publications_list.add(publ)

    def dump(self, out_folder=""):
        # pkl dump stuff
        file = out_folder + self.kind
        with open(file+".pkl", 'wb') as ar:
            pickle.dump(self.publications_list, ar)


    def write(self, out_folder=""):
        # write informations in a file
        file = out_folder + self.kind

        with open(file+".csv", 'w') as file:
            for publication in self.publications_list:
                line = ""
                line += publication.cnpq + '\t'
                line += str(publication.serial) + '\t'
                line += publication.title + '\t'
                line += str(publication.year) + '\t'

                for authors in publication.authors:
                    line += authors + ','

                line = line[:-1]

                line += '\t' + publication.vehicle
                line += '\n'
                file.writelines(line)



"""
evento = congress
periódicos = journal
veiculo = ?
"""
