"""
 Print all questions of ChatBot in questions.txt
"""

import os

ROOT_DIR = os.getcwd()
DIR = '%s/%s.xml' % (ROOT_DIR, "ia_start")
ARCH = open(DIR, "r")
ARCH.seek(0)
ARCHIVES = []
for line in ARCH.readlines():
    if "<learn>" in line:
        ini = line.find("<learn>") + 7
        fin = line.find("</learn>")
        ARCHIVES.append(line[ini:fin])
ARCH.close()
PARTNERS = open(ROOT_DIR + "/questions.txt", "w")
for archive in ARCHIVES:
    DIR = '%s/%s' % (ROOT_DIR, archive)
    PARTNERS.write("\n-----" + archive + "-----\n" + "\n")
    ARCH = open(DIR, "r")
    ARCH.seek(0)
    for line in ARCH.readlines():
        if "<pattern>" in line:
            ini = line.find("<pattern>") + 9
            fin = line.find("</pattern>")
            PARTNERS.write(line[ini:fin] + "\n")
    ARCH.close()
PARTNERS.close()
