""" List unanswered questions through the .bd"""

import sqlite3

CONN = sqlite3.connect('show_unanswered.bd')
CONN_CURSOR = CONN.cursor()
CONN_CURSOR.execute('SELECT * FROM preguntas')
for row in list(CONN_CURSOR):
    print row[3]
CONN.commit()
CONN_CURSOR.close()
CONN.close()
