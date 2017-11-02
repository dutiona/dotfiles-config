#!/usr/bin/env python3

"""
BibTex parser.
"""

import json
import unicodedata
import subprocess
import sys

from datetime import datetime
from dateutil import parser as dateparser
from urllib.request import urlopen

# local import
from bibtexparser import BibTexParser
from simplemediawiki import MediaWiki

import logging
from logging import debug, info, warning, error
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

import difflib
diff = difflib.Differ()

MINDATETIME = datetime(1, 1, 1)

months = (
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
        )


def pretty_print(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

def clean_old_publications(wiki, publications):
    """
    Delete old publication pages.
    """
    r = wiki.call2(action="query", list="categorymembers", cmtitle="Category:Publications", cmlimit=5000)
    for page in r['query']['categorymembers']:
        if page['title'] not in publications:
            deletetoken = wiki.get_deletetoken(page['title'])
            info("Deleting page '{}'".format(page['title']))
            wiki.call2(action="delete", title=page['title'], token=deletetoken)

def clean_old_redirections(wiki, redirections):
    """
    Delete old publication redirection pages.
    """
    r = wiki.call2(action="query", list="categorymembers", cmtitle="Category:PublicationRedirected", cmlimit=5000)
    for page in r['query']['categorymembers']:
        if page['title'] not in redirections:
            deletetoken = wiki.get_deletetoken(page['title'])
            info("Deleting page '{}'".format(page['title']))
            wiki.call2(action="delete", title=page['title'], token=deletetoken)

def record_to_bibtex(record, bibtex):
    """
    Extract a textual representation of a bibtex entry.
    Some private fields are ignored like 'lrdenewsdate'.
    """
    return subprocess.check_output(
            ["bibtool", "-q", "-i", bibtex, "-X", record['id'], 
                "--", "delete.field = lrdepaper",
                "--", "delete.field = lrdeslides",
                "--", "delete.field = lrdeposter",
                "--", "delete.field = lrdeinc",
                "--", "delete.field = lrdekeywords",
                "--", "delete.field = lrdeprojects",
                "--", "delete.field = lrdenewsdate",
                "--", "delete.field = urllrde"
                ],
            universal_newlines = True)

def test_url(url):
    try:
        response = urlopen(url)
        return True
    except Exception:
        return False

def process(wiki, bibtex):
    publications = set()
    redirections = set()

    def parse_author(author):
        t=author.split(', ')
        if len(t) > 1:
            return "{firstname} {lastname}".format(firstname=t[1], lastname=t[0])
        return author

    with open(bibtex) as filehandle:
        parser = BibTexParser(filehandle)
        records, metadata = parser.parse()

    if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
        debug("Dump json conversion of {0} in {0}.json".format(bibtex))
        with open("{}.json".format(bibtex), "w") as filehandle:
            filehandle.write(json.dumps(records, indent=4, separators=(',', ': ')))

    for record in records:
        if "id" not in record or "year" not in record or "title" not in record:
            continue

        news = "{{Publication\n"

        # Ignore submitted papers
        if "note" in record and record["note"] == "Submitted":
            news += "| published = false\n"
        else:
            news += "| published = true\n"


        # Search for a news date using the field lrdenewsdate or a combination of the fields month/year
        newsdate = False
        if "lrdenewsdate" in record:
            try:
                newsdatetime = dateparser.parse(record['lrdenewsdate'], default=MINDATETIME)
                if newsdatetime != MINDATETIME:
                    newsdate = newsdatetime.strftime("%Y-%m-%d")
            except ValueError:
                warning("Cannot parse the date '{}' in '{}'".format(record['lrdenewsdate'], record['id']))
        if not newsdate:
            debug("The entry '{}' doesn't have a lrdenewsdate".format(record['id']))
            year = record['year']
            if "month" in record and record['month'] in months:
                month = record['month']
            else:
                month = "jan"
            newsdate = datetime.strptime("{year}-{month}".format(month=month, year=year), "%Y-%b").strftime("%Y-%m-%d")
        news += "| date = {0}\n".format(newsdate)

        # Convert all bibtex fields into a mediawiki template parameter
        for key, value in record.items():
            if key in ("month", "year"):
                pass
            elif key == "author":
                news += "| authors = {authors}\n".format(authors=", ".join([parse_author(author['name']) for author in value]))
            elif key == "editor":
                news += "| editors = {editors}\n".format(editors=", ".join([parse_author(editor['name']) for editor in value]))
            elif key == "journal":
                value = value['name']
                value = value.replace("\n", " ")
                news += "| journal = {journal}\n".format(journal=value)
            elif key == "identifier":
                news += "| identifier = {0}:{1}\n".format(value[0]['type'], value[0]['id'])
            elif key in ("lrdepaper", "lrdeslides", "lrdeposter"):
                if test_url(value):
                    news += "| {} = {}\n".format(key, value)
                else:
                    warning("Broken link '{}' in '{}'".format(value, record['id']))
            elif key == "lrdevideos":
                videos = value.split(",")
                news += "| {key} = {widgets}".format(key=key, widgets=", ".join())
            elif isinstance(value, str):
                value = value.replace("\n", " ")
                news += "| {key} = {value}\n".format(key=key, value=value)

        # Add the bibtex entry
        bibtex_entry = record_to_bibtex(record, bibtex)
        bibtex_entry = bibtex_entry.replace("{","<nowiki>{</nowiki>")
        bibtex_entry = bibtex_entry.replace("}","<nowiki>}</nowiki>")
        news += "| bibtex = {}\n".format(bibtex_entry)
        news += "}}"

        # Update (if needed) the publication page
        page_title="Publications/{}".format(record['id'])
        old_news = wiki.get_page(page_title)
        news = unicodedata.normalize('NFKD', news)
        old_news = unicodedata.normalize('NFKD', old_news)
        if old_news != news:
            info("Update publication {0}".format(page_title))
            debug("Diff:\n" + "".join(list(diff.compare(old_news.splitlines(1), news.splitlines(1)))))
            wiki.update_page(title=page_title, content=news)
        publications.add(page_title)

        # Leave a redirect from old pages that use urllrde
        if "urllrde" in record and record['urllrde'] != record['id']:
            redirect_page_title="Publications/{}".format(record['urllrde'])
            wiki.update_page(title=redirect_page_title, content="#REDIRECT [[{}]]\n[[Category:PublicationRedirected]]".format(page_title))
            redirections.add(redirect_page_title)


    clean_old_publications(wiki, publications)
    clean_old_redirections(wiki, redirections)

def main():
    wiki = MediaWiki('https://www.lrde.epita.fr/api.php')
    wiki.login('Bot', 'raiQuaef4hooyu7eoZ6t', 'local')
    info("Connected to %s" % wiki.call2(action='query', meta='siteinfo')['query']['general']['sitename'])

    # pretty_print(wiki.call2(action="query", list="categorymembers", cmtitle="Category:Publications", cmlimit=5000))
    for arg in sys.argv[1:]:
        process(wiki, arg)
        sys.exit()

    wiki.logout()

if __name__ == '__main__':
    main()
