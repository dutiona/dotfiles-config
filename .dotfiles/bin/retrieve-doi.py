#!/usr/bin/env python3

import json
import sys
import re

from urllib.parse import quote_plus, unquote
from urllib.request import urlopen

from bibtexparser import BibTexParser

def process(bibtex):
    with open(bibtex) as filehandle:
        parser = BibTexParser(filehandle)
        records, metadata = parser.parse()

        for record in records:
            print(record['id'])
            title = record['title'].replace('\n', ' ')
            firstauthor = record['author'][0]['name'].replace(',', '')

            # print(title)
            # print(firstauthor)

            url = "http://gen.lib.rus.ec/scimag/?s={}+{}&redirect=0".format(quote_plus(title), quote_plus(firstauthor))
            # print(url)

            try:
                html = urlopen(url).read().decode('utf-8')
                # print(html)
                m = re.search('href="/scimag/get\.php\?doi=([^"]+)"', html)

                if m:
                    print("DOI: {}".format(unquote(m.group(1))))
                else:
                    print("No DOI found")
                print()
            except:
                pass

def main():
    for arg in sys.argv[1:]:
        process(arg)

if __name__ == '__main__':
    main()
