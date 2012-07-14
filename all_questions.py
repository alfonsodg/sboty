"""
 Print all questions of ChatBot in questions.txt
"""

import os

ROOT_DIR = os.getcwd()
DIR = '%s/%s.xml' % (ROOT_DIR, "ia_start")
ARCHI = open(DIR, "r")
ARCHI.seek(0)
ARCHIVOS = []
for line in ARCHI.readlines():
    if "<learn>" in line:
        ini = line.find("<learn>") + 7
        fin = line.find("</learn>")
        ARCHIVOS.append(line[ini:fin])
ARCHI.close()
PATTNERS = open(ROOT_DIR + "/questions.txt", "w")
for archivo in ARCHIVOS:
    DIR = '%s/%s' % (ROOT_DIR, archivo)
    PATTNERS.write("\n-----" + archivo + "-----\n" + "\n")
    ARCHI = open(DIR, "r")
    ARCHI.seek(0)
    for line in ARCHI.readlines():
        if "<pattern>" in line:
            ini = line.find("<pattern>") + 9
            fin = line.find("</pattern>")
            PATTNERS.write(line[ini:fin] + "\n")
    ARCHI.close()
PATTNERS.close()
