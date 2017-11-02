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

def pretty_print(data):
    print(json.dumps(data, indent=2, separators=(',', ': ')))

class teamcitytest(object):
    def __init__(self, name):
        self._name = name

    def __enter__(self):
        print("##teamcity[testStarted name='{}']".format(self._name))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("##teamcity[testFinished name='{}']".format(self._name))

    def fail(self, message, details):
        print("##teamcity[testFailed name='{}' message='{}' details='{}']".format(self._name, message, details))

def clean_old_reports(wiki, reports, category):
    """
    Delete old reports pages.
    """
    r = wiki.call2(action="query", list="categorymembers", cmtitle="Category:{}".format(category), cmlimit=5000)
    for page in r['query']['categorymembers']:
        if page['title'] not in reports:
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

def test_url(url):
    try:
        response = urlopen(url)
        return True
    except Exception:
        return False


def process(wiki, bibtex):
    reports = set()
    reports_fr = set()
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
        if "id" not in record:
            error("Missing bibtex id !")
            continue

        with teamcitytest(record["id"]) as tt:
            if "title" not in record:
                warning("Missing title")
                tt.fail("Missing title key", "")
                continue
            if "abstract" not in record:
                warning("Missing abstract")
                tt.fail("Missing abstract attribute", "")
                continue
            if "titre" not in record:
                warning("Missing titre")
                tt.fail("Missing titre key", "")
                continue
            if "resume" not in record:
                warning("Missing resume")
                tt.fail("Missing resume attribute", "")
                continue

            report = "{{CSIReport\n"
            report_fr = "{{CSIReportFR\n"

            # Convert all bibtex fields into a mediawiki template parameter
            for key, value in record.items():
                if key == "author":
                    report += "| authors = {authors}\n".format(authors=", ".join([parse_author(author['name']) for author in value]))
                    report_fr += "| authors = {authors}\n".format(authors=", ".join([parse_author(author['name']) for author in value]))
                elif key in ("lrdepaper", "lrdeslides", "lrdeposter"):
                    if test_url(value):
                        report += "| {} = {}\n".format(key, value)
                        report_fr += "| {} = {}\n".format(key, value)
                    else:
                        warning("Broken link '{}' in '{}'".format(value, record['id']))
                        tt.fail("Broken link '{}' in '{}'".format(value, record['id']), "")
                elif key in ("id", "year", "number", "type", "lrdekeywords", "lrdeprojects", "lrdeinc"):
                    report += "| {key} = {value}\n".format(key=key, value=value.replace('\n',' '))
                    report_fr += "| {key} = {value}\n".format(key=key, value=value.replace('\n',' '))
                elif key in ("title", "abstract"):
                    report += "| {key} = {value}\n".format(key=key, value=value.replace('\n',' '))
                elif key in ("titre", "resume"):
                    report_fr += "| {key} = {value}\n".format(key=key, value=value.replace('\n',' '))

            report += "}}"
            report_fr += "}}"

            # Update (if needed) the CSI report pages
            page_title="Publications/{}".format(record['id'])
            old_report = wiki.get_page(page_title)
            report = unicodedata.normalize('NFKD', report)
            old_report = unicodedata.normalize('NFKD', old_report)
            if old_report != report:
                info("Update report {0}".format(page_title))
                debug("Diff:\n" + "".join(list(diff.compare(old_report.splitlines(1), report.splitlines(1)))))
                wiki.update_page(title=page_title, content=report)
            reports.add(page_title)

            # Update (if needed) the CSI report pages (french version)
            page_title_fr="Publications/{}/fr".format(record['id'])
            old_report_fr = wiki.get_page(page_title_fr)
            report_fr = unicodedata.normalize('NFKD', report_fr)
            old_report_fr = unicodedata.normalize('NFKD', old_report_fr)
            if old_report_fr != report_fr:
                info("Update report {0}".format(page_title_fr))
                debug("Diff:\n" + "".join(list(diff.compare(old_report_fr.splitlines(1), report_fr.splitlines(1)))))
                wiki.update_page(title=page_title_fr, content=report_fr)
            reports_fr.add(page_title_fr)

            # Leave a redirect from old pages that use urllrde
            if "urllrde" in record and record['urllrde'] != record['id']:
                redirect_page_title="Publications/{}".format(record['urllrde'])
                wiki.update_page(title=redirect_page_title, content="#REDIRECT [[{}]]\n[[Category:PublicationRedirected]]".format(page_title))
                redirections.add(redirect_page_title)

    clean_old_reports(wiki, reports, "CSIReports")
    clean_old_reports(wiki, reports_fr, "CSIReportsFR")
    clean_old_redirections(wiki, redirections)


def main():
    wiki = MediaWiki('https://www.lrde.epita.fr/api.php')
    wiki.login('Bot', 'raiQuaef4hooyu7eoZ6t', 'local')
    info("Connected to %s" % wiki.call2(action='query', meta='siteinfo')['query']['general']['sitename'])

    # pretty_print(wiki.call2(action="query", list="categorymembers", cmtitle="Category:CSIReports", cmlimit=5000))
    for arg in sys.argv[1:]:
        process(wiki, arg)
        sys.exit()

    wiki.logout()

if __name__ == '__main__':
    main()
