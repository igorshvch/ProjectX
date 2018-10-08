import sqlite3

def init_db(path):
    connection = sqlite3.connect(str(path))
    with open(
        r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\schema.sql'
    ) as file:
        connection.executescript(file.read())
    connection.commit()
    return connection