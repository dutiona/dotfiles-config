#!/bin/python3

import csv
import sys
import json

from simplemediawiki import MediaWiki

def pretty_print(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

teachers = {
        'DURET-LUTZ.Alexandre': '[[User:Adl]]',
        'RICOU.Olivier': '[[User:Ricou]]',
        'GERAUD.Thierry': '[[User:Theo]]',
        'LEVILLAIN.Roland': '[[User:Roland]]',
        'DEHAK.Reda': '[[User:Reda]]',
        'DEMAILLE.Akim': '[[User:Akim]]',
        'VERNA.Didier': '[[User:Didier]]',
        'FABRIZZIO.Johnatan': '[[User:Jonathan]]',
        'DEMOULINS.Clément': '[[User:Cd]]'
}

audiences = {
        '': 'InfoSub',
        '': 'InfoSpé',
        '': 'Tronc-commun',
        '': 'Majeure',
        '': 'Apprentis',
        '': 'Cycle Ing',
        '': 'CSI',
        '': 'SCIA'
}

labels = {
        'intitule': 'title',
        'code': 'acronym',
        'enseignant-officiel': 'teacher',
        'annee': 'period',
        'orientation': 'audience',
}

def process(wiki, csvfile):
    reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    for row in reader:
        if reader.line_num == 1:
            fields = row
            continue
        items = zip(fields, row)
        course = "{{Course\n"
        data = {}
        for (name, value) in items:
            name = name.lower()
            value = value.strip()
            if name in labels:
                name = labels[name]
                data[name] = value
                if name == 'teacher':
                    course += "| {} = {}\n".format(name, teachers[value])
                else:
                    course += "| {} = {}\n".format(name, value)
        course += "}}\n"
        print(course)
        #title = "{} ({})".format(data['intitule'], data['code'])
        #title = title.replace('[', '').replace(']', '')
        #pretty_print(wiki.update_page(title=title, content=course))

def main():
    wiki = MediaWiki('https://www.lrde.epita.fr/api.php')
    wiki.login('Bot', 'raiQuaef4hooyu7eoZ6t', 'local')
    print("# Connected to %s" % wiki.call2(action='query', meta='siteinfo')['query']['general']['sitename'])

    for arg in sys.argv[1:]:
        with open(arg) as csvfile:
            process(wiki, csvfile)
        sys.exit()

    wiki.logout()

if __name__ == '__main__':
    main()
