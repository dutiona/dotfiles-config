#!/usr/bin/env python2

import os
import codecs
import xdg.DesktopEntry

class DesktopEntry(xdg.DesktopEntry.DesktopEntry):
    def __hash__(self):
        return hash(self.filename)

items = []
categories = {
        "Multimedia"             : set(),
        "Development"            : set(),
        "Education"              : set(),
        "Game"                   : set(),
        "Graphics"               : set(),
        "Network"                : set(),
        "Office"                 : set(),
        "Settings"               : set(),
        "System"                 : set(),
        "Utility"                : set()
        }
categories_map = {
        "AudioVideo"             : "Multimedia",
        "Audio"                  : "Multimedia",
        "Video"                  : "Multimedia",
        "Development"            : "Development",
        "Education"              : "Education",
        "Game"                   : "Game",
        "Graphics"               : "Graphics",
        "Network"                : "Network",
        "Office"                 : "Office",
        "Settings"               : "Settings",
        "System"                 : "Sytem",
        "Utility"                : "Utility",
        "Building"               : "Development",
        "Debugger"               : "Development",
        "IDE"                    : "Development",
        "GUIDesigner"            : "Development",
        "Profiling"              : "Development",
        "RevisionControl"        : "Development",
        "Translation"            : "Development",
        "Calendar"               : "Office",
        "ContactManagement"      : "Office",
        "Database"               : "Development",
        "Dictionary"             : "Office",
        "Chart"                  : "Office",
        "Email"                  : "Network",
        "Finance"                : "Office",
        "FlowChart"              : "Office",
        "PDA"                    : "Office",
        "ProjectManagement"      : "Development",
        "Presentation"           : "Office",
        "Spreadsheet"            : "Office",
        "WordProcessor"          : "Office",
        "2DGraphics"             : "Graphics",
        "VectorGraphics"         : "Graphics",
        "RasterGraphics"         : "Graphics",
        "3DGraphics"             : "Graphics",
        "Scanning"               : "Graphics",
        "OCR"                    : "Graphics",
        "Photography"            : "Graphics",
        "Publishing"             : "Graphics",
        "Viewer"                 : "Graphics",
        "TextTools"              : "Utility",
        "DesktopSettings"        : "Settings",
        "HardwareSettings"       : "Settings",
        "Printing"               : "Settings",
        "PackageManager"         : "Settings",
        "Dialup"                 : "Network",
        "InstantMessaging"       : "Network",
        "Chat"                   : "Network",
        "IRCClient"              : "Network",
        "FileTransfer"           : "Network",
        "HamRadio"               : "Multimedia",
        "News"                   : "Network",
        "P2P"                    : "Network",
        "RemoteAccess"           : "Network",
        "Telephony"              : "Network",
        "TelephonyTools"         : "Utility",
        "VideoConference"        : "Network",
        "WebBrowser"             : "Network",
        "WebDevelopment"         : "Development",
        "Midi"                   : "Multimedia",
        "Mixer"                  : "Multimedia",
        "Sequencer"              : "Multimedia",
        "Tuner"                  : "Multimedia",
        "TV"                     : "Multimedia",
        "AudioVideoEditing"      : "Multimedia",
        "Player"                 : "Multimedia",
        "Recorder"               : "Multimedia",
        "DiscBurning"            : "Multimedia",
        "ActionGame"             : "Game",
        "AdventureGame"          : "Game",
        "ArcadeGame"             : "Game",
        "BoardGame"              : "Game",
        "BlocksGame"             : "Game",
        "CardGame"               : "Game",
        "KidsGame"               : "Game",
        "LogicGame"              : "Game",
        "RolePlaying"            : "Game",
        "Simulation"             : "Game",
        "SportsGame"             : "Game",
        "StrategyGame"           : "Game",
        "Art"                    : "Education",
        "Construction"           : "Education",
        "Music"                  : "Multimedia",
        "Languages"              : "Education",
        "Science"                : "Education",
        "ArtificialIntelligence" : "Education",
        "Astronomy"              : "Education",
        "Biology"                : "Education",
        "Chemistry"              : "Education",
        "ComputerScience"        : "Education",
        "DataVisualization"      : "Education",
        "Economy"                : "Education",
        "Electricity"            : "Education",
        "Geography"              : "Education",
        "Geology"                : "Education",
        "Geoscience"             : "Education",
        "History"                : "Education",
        "ImageProcessing"        : "Education",
        "Literature"             : "Education",
        "Math"                   : "Education",
        "NumericalAnalysis"      : "Education",
        "MedicalSoftware"        : "Education",
        "Physics"                : "Education",
        "Robotics"               : "Education",
        "Sports"                 : "Education",
        "ParallelComputing"      : "Education",
        "Amusement"              : "",
        "Archiving"              : "Utility",
        "Compression"            : "Utility",
        "Electronics"            : "",
        "Emulator"               : "System",
        "Engineering"            : "",
        "FileTools"              : "Utility",
        "FileManager"            : "System",
        "TerminalEmulator"       : "System",
        "Filesystem"             : "System",
        "Monitor"                : "System",
        "Security"               : "Settings",
        "Accessibility"          : "Settings",
        "Calculator"             : "Utility",
        "Clock"                  : "Utility",
        "TextEditor"             : "Utility",
        "Documentation"          : "",
        "Core"                   : "",
        "KDE"                    : "",
        "GNOME"                  : "",
        "GTK"                    : "",
        "Qt"                     : "",
        "Motif"                  : "",
        "Java"                   : "",
        "ConsoleOnly"            : ""
        }
applications = "/usr/share/applications/"

for f in os.listdir(applications):
    try:
        entry = DesktopEntry(applications + f)
        if not entry.getNoDisplay() and not entry.getHidden():
            for cat in entry.getCategories():
                try:
                    category = categories[categories_map[str(cat)]]
                    category.add(entry)
                except KeyError:
                    pass
    except:
        pass

menu = codecs.open(os.environ["HOME"] + "/.config/wmfs/menu", "w", encoding="utf_8")

menu.write("""
# Menu applications
[set_menu]
    name = "Applications"
    align = "left"
    fg_focus  = "#191919" bg_focus  = "#7E89A2"
    fg_normal = "#9F9AB3" bg_normal = "#191919"\n\n""")
menu.write("\n".join(
    ("    [item] name = \"%s\" submenu = \"%s\" [/item]" % (c, c)
        for c in categories.iterkeys())
    ))
menu.write("\n[/set_menu]\n\n")

for c in categories.iterkeys():
#    print(c + ": " + ", ".join((e.getName() for e in categories[c])) + "\n")
    menu.write(u"\n# Category: %s\n" % (c,))
    menu.write(u"""[set_menu]
    name = "%s"
    align = "left"
    fg_focus  = "#191919" bg_focus  = "#7E89A2"
    fg_normal = "#9F9AB3" bg_normal = "#191919"\n\n""" % (c,))
    menu.write(u"\n".join(
        (u"    [item] name = \"%s\" func = \"spawn\" cmd = \"%s\" [/item]" % (e.getName(), e.getExec())
            for e in categories[c])
        ))
    menu.write(u"\n[/set_menu]\n")

menu.close()
