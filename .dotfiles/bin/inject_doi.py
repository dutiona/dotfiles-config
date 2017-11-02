#!/usr/bin/python3

import sys
import gzip
import xml.etree.ElementTree as ET

from bibtexparser import BibTexParser

def process(bib_path, dblp_path):
    # with open(bib_path) as fd:
    #     parser = BibTexParser(fd)
    #     records, metadata = parser.parse()

    # with gzip.open(dblp_path) as fd:
    ET.parse(dblp_path)

    # for record in records:
    #     print(record['id'])


def main():
    process(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
