import sqlite3

INSERT_STMT = {
    'acts': 'INSERT INTO acts (act) VALUES (?)',
    'wordraw' : 'INSERT INTO wordraw (word) VALUES (?)',
    'wordnorm' : 'INSERT INTO wordnorm (word) VALUES (?)',
    'wordmapping': 'INSERT INTO wordmapping (raww, norm) VALUES (?, ?)',
    'docindraw': 'INSERT INTO docindraw (word, postinglist) VALUES (?, ?)',
    'docindnorm': 'INSERT INTO docindnorm (word, postinglist) VALUES (?, ?)'
}


def init_db(path):
    connection = sqlite3.connect(str(path))
    with open(r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\schema.sql') as file:
        connection.executescript(file.read())
    connection.commit()
    return connection

def fulfill_tables(connection, dct):
    cursor = connection.cursor()
    tables = cursor.execute(
        'SELECT name FROM sqlite_master WHERE type="table"'
    ).fetchall()
    for table_name in tables: #('wordmapping', 'docindraw', 'docindnorm'):
        data = dct[table_name[0]]
        statement = INSERT_STMT[table_name[0]]
        cursor.executemany(
            statement, data
        )