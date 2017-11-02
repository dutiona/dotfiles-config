#!/bin/python3

import csv
import sys
import json

from simplemediawiki import MediaWiki

def pretty_print(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

def process(wiki, f):
    data = json.loads(f.read())
    for entry in data:
        news = "{{News\n"
        news += "|title={}\n".format(entry['title'])
        news += "|subtitle={}\n".format(entry['subtitle'])
        news += "|date={}\n".format(entry['date'])
        news += "}}\n"
        # print(news)
        pretty_print(wiki.update_page(title=entry['page'], content=news))

def main():
    wiki = MediaWiki('https://www2.lrde.epita.fr/api.php')
    wiki.login('Bot', 'raiQuaef4hooyu7eoZ6t', 'local')
    print("# Connected to %s" % wiki.call2(action='query', meta='siteinfo')['query']['general']['sitename'])

    for arg in sys.argv[1:]:
        with open(arg) as f:
            process(wiki, f)
        sys.exit()

    wiki.logout()

if __name__ == '__main__':
    main()
