#!/bin/python3

from simplemediawiki import MediaWiki

import timeit
import sys
import re
import datetime
from dateutil import parser
import json
from sh import bibtool
import tempfile
import concurrent.futures

import logging
from logging import debug
#logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

lrde_bib = "/home/clement/Documents/lrde-publis-share/bib/lrde.bib"

def parse(f):
    news = False
    data = f.read()
    db = []
    m = re.findall("(?:^---\+\+ (\d{4}))|(?:\[\[Publications\.(\d[^]]*)\]\[(?:.|\n)*? (Jan\w*|Feb\w*|Mar\w*|Apr\w*|May|June?|July?|Aug\w*|Sep\w*|Oct\w*|Nov\w*|Dec\w*) (\d{1,2}))", data, flags=re.MULTILINE)
    for i in m:
        if i[0]:
            year = i[0]
        elif i[1]:
            urllrde = i[1]
            month = i[2]
            day = i[3]
            try:
                date = parser.parse("{} {} {}".format(day, month, year)).strftime("%Y-%m-%d")
            except:
                debug("{} - {} {} {}".format(urllrde, day, month, year))
            db.append({'urllrde': urllrde, 'date': date})
        else:
            debug(str(i))
    debug(json.dumps(db, sort_keys=True, indent=4, separators=(',', ': ')))
    return db

def process_entry(entry):
    debug(entry)
    return bibtool("-i", lrde_bib,
            "--", "select.by.string = {{urllrde \"{}\"}}".format(entry['urllrde']),
            "--", "add.field = {{lrdenewsdate=\"{}\"}}".format(entry['date']))

def process(db, workers=1):
    entries_bib = []
    fd, tmp_file = tempfile.mkstemp(suffix=".bib")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        for entry_bib in executor.map(process_entry, db):
            entries_bib.append(str(entry_bib))
    with open(tmp_file, "w") as f:
        f.write("".join(entries_bib))

    new_lrde_bib = str(bibtool("-i", tmp_file, "-i", lrde_bib,
            "--", "sort={on}",
            "--", "check.double.delete=ON",
            "--", "check.double=ON"))
    print(new_lrde_bib)

def test(worker):
    with open(sys.argv[1], "r", encoding="latin1") as f:
        process(parse(f), worker)

def main():
    with open(sys.argv[1], "r", encoding="latin1") as f:
        process(parse(f), 8)
    #print(timeit.repeat('test(1)', setup="from __main__ import test,process,parse,process_entry", number=1, repeat=5))
    #print(timeit.repeat('test(2)', setup="from __main__ import test,process,parse,process_entry", number=1, repeat=5))
    #print(timeit.repeat('test(4)', setup="from __main__ import test,process,parse,process_entry", number=1, repeat=5))
    #print(timeit.repeat('test(8)', setup="from __main__ import test,process,parse,process_entry", number=1, repeat=5))
    #print(timeit.repeat('test(16)', setup="from __main__ import test,process,parse,process_entry", number=1, repeat=5))

if __name__ == '__main__':
    main()

