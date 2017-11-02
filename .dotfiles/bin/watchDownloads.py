#!/usr/bin/python2
# -*- coding: utf-8 -*-

import pyinotify
import os
import re
import subprocess

wm = pyinotify.WatchManager()
mask = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE | pyinotify.IN_DELETE

"""
Chaque fichiers déplacés dans un sous-dossier "Saison ??" du dossier surveillé est
considéré comme nouveau (date de dernière modification mise à jour).
"""
class HandleEvents(pyinotify.ProcessEvent):
    def process_IN_MOVED_TO(self, event):
        if not event.dir and re.match(".*/Saison [0-9]+$", event.path) <> None:
            with file(event.pathname, "a"):
                print("MovedTo : %s/%s" % (event.path, event.name))
                os.utime(event.pathname, None)
#                subprocess.Popen("last", shell=True)

    def process_IN_CREATE(self, event):
        pass
#        print("Create : %s [isDir=%s]" % (event.pathname, event.dir))

    def process_IN_DELETE(self, event):
#        pass
        if not event.dir and (event.name.endswith("avi") or event.name.endswith("mkv")):
            print("Delete : %s [isDir=%s]" % (event.pathname, event.dir))
#            subprocess.Popen("last", shell=True)


def main():
    p = HandleEvents()
    notifier = pyinotify.Notifier(wm, p)

    wdd = wm.add_watch('/home/clement/Download/Series', mask, rec=True, auto_add=True)
    notifier.loop()

main()
