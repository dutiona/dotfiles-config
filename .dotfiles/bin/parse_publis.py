#!/usr/bin/env python3

from sh import find, bibtool
import re
import os
import tempfile

conv_project={
        "%LOGOOLENA%": "Olena",
        "%LOGOURBI%": "URBI",
        "%LOGOVAUCANSON%": "Vaucanson",
        "%LOGOTIGER%": "Tiger",
        "%LOGOAPMC%": "APMC",
        "%LOGOSPOT%": "Spot",
        }
conv_keyword={
        "%LOGOIMA%": "Image",
        "%LOGOSE%": "Software engineering",
        "%LOGOLRDENANO%": "LRDE",
        }

lrde_bib = "/home/clement/Documents/lrde-publis-share/bib/lrde.bib"

conv_twiki_variables = {
        "%LRDEDOWNLOAD%": "http://www.lrde.epita.fr/dload/",
        "%WWWLRDE%": "http://www.lrde.epita.fr/",
        }

def process_url(rawurl):
    url = rawurl
    for key, value in conv_twiki_variables.items():
        url = url.replace(key, value)
    return url

def main():
    files = find(".", "-name", "2*", "-not", "-name", "*Seminar*").split("\n")[0:-1]
    search_logos = re.compile("name=\"Logo\".* value=\"(.*)\"")
    search_urls = re.compile("\[\[([^]]+)\](?:\[[^]]+\])?\]")

    entries_bib = []

    for f in files:
        keywords = set()
        projects = set()
        paper = None
        slides = None
        poster = None
        newsdate = None

        urllrde = f[2:-4]
        fd = open(f, encoding="latin1")
        content = fd.read()

        m = search_logos.search(content)
        if m:
            for k in m.group(1).split(", "):
                if k in conv_project:
                    projects.add(conv_project[k])
                if k in conv_keyword:
                    keywords.add(conv_keyword[k])

        m = search_urls.search(content)
        if m:
            for rawurl in m.groups():
                url = process_url(rawurl)
                if url.endswith("FIXME.pdf"):
                    pass
                elif "slide" in url:
                    slides = slides
                    print("#   * slides [{}]".format(url))
                elif "poster" in url:
                    poster = url
                    print("#   * poster [{}]".format(url))
                elif url.endswith(".pdf"):
                    paper = url
                    print("#   * paper [{}]".format(url))
                #else:
                    #print("#  - {}".format(url))

        bibtool_cmd = bibtool.bake("-i", lrde_bib,
                "--", "select.by.string = {{urllrde \"{}\"}}".format(urllrde))
        if len(projects) > 0:
            bibtool_cmd = bibtool_cmd.bake("--", "add.field = {{lrdeprojects=\"{}\"}}".format(", ".join(projects)))
        if len(keywords) > 0:
            bibtool_cmd = bibtool_cmd.bake("--", "add.field = {{lrdekeywords=\"{}\"}}".format(", ".join(keywords)))
        if paper:
            bibtool_cmd = bibtool_cmd.bake("--", "add.field = {{lrdepaper=\"{}\"}}".format(paper))
        if poster:
            bibtool_cmd = bibtool_cmd.bake("--", "add.field = {{lrdeposter=\"{}\"}}".format(poster))
        if slides:
            bibtool_cmd = bibtool_cmd.bake("--", "add.field = {{lrdeslides=\"{}\"}}".format(slides))


        entry_bib = bibtool_cmd()
        print("# {} [{}]".format(urllrde, len(str(entry_bib))))
        entries_bib.append(str(entry_bib))

    fd, tmp_file = tempfile.mkstemp(suffix=".bib")
    with open(tmp_file, "w") as f:
        f.write("".join(entries_bib))

    new_lrde_bib = str(bibtool("-i", tmp_file, "-i", lrde_bib,
            "--", "sort={on}",
            "--", "check.double.delete=ON",
            "--", "check.double=ON"))
    print(new_lrde_bib)
    #print("".join(entries_bib))
    os.remove(tmp_file)

if __name__ == '__main__':
    main()
