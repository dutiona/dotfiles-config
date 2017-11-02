#!/usr/bin/env python3

import argparse
import os.path
import json

from simplemediawiki import MediaWiki

import logging
from logging import debug, info, warning, error
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def pretty_print(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

def main():
    parser = argparse.ArgumentParser(description='Upload files to mediawiki.')
    parser.add_argument('files', metavar='File', nargs='+', help='uploaded files')
    args = parser.parse_args()

    wiki = MediaWiki('https://www.lrde.epita.fr/api.php')
    wiki.login('Bot', 'raiQuaef4hooyu7eoZ6t', 'local')
    info("Connected to %s" % wiki.call2(action='query', meta='siteinfo')['query']['general']['sitename'])

    edittoken = wiki.get_edittoken(os.path.basename(args.files[0]))
    for f in args.files:
        with open(f, 'rb') as fd:
            content = fd.read()
            print(len(content))
            r = wiki.call( { 'action': 'upload', 'filename': os.path.basename(f), 'file': content, 'token': edittoken } )
            pretty_print(r)

    wiki.logout()

if __name__ == '__main__':
    main()
