import sqlite3
import pathlib

INSERT_STMT = {
    'acts': 'INSERT INTO acts (act) VALUES (?)',
    'wordraw' : 'INSERT INTO wordraw (word) VALUES (?)',
    'wordnorm' : 'INSERT INTO wordnorm (word) VALUES (?)',
    'wordmapping': 'INSERT INTO wordmapping (raww, norm) VALUES (?, ?)',
    'docindraw': (
        'INSERT INTO docindraw (word, postinglist, docfreq) VALUES (?, ?, ?)'
    ),
    'docindnorm': (
        'INSERT INTO docindnorm (word, postinglist, docfreq) VALUES (?, ?, ?)')
        ,
    'termfreqraw': (
        'INSERT INTO termfreqraw (actid, word, termfreq) VALUES (?, ?, ?)'
    ),
    'termfreqnorm': (
        'INSERT INTO termfreqnorm (actid, word, termfreq) VALUES (?, ?, ?)'
    ),
    'tfidfraw': (
        'INSERT INTO tfidfraw (actid, vector) VALUES (?, ?)'
    ),
    'tfidfnorm': (
        'INSERT INTO tfidfnorm (actid, vector) VALUES (?, ?)'
    )
}


def init_db(path, schema_path=None):
    connection = sqlite3.connect(str(path))
    if schema_path:
        with open(schema_path) as file:
            connection.executescript(file.read())
    else:
        with open(r'C:\Users\EA-ShevchenkoIS\AppData\Local\Continuum\anaconda3\ProjectX\schema.sql') as file:
            connection.executescript(file.read())
    connection.commit()
    return connection

def get_con(path):
    if pathlib.Path(path).exists():
        return sqlite3.connect(str(path))
    else:
        raise ValueError('{} - no such file'.format(path))

def fulfill_tfidf_table(connection, mtrx, mode='raw'):
    cursor = connection.cursor()
    if mode == 'raw':
        table = 'tfidfraw'
    elif mode == 'norm':
        table = 'tfidfnorm'
    cursor.executemany(
        '''
        INSERT INTO {tb} (vector) VALUES (?)
        '''.format(tb=table),
        mtrx
    )

def fulfill_tables_with_dct(connection, dct):
    cursor = connection.cursor()
    tables = cursor.execute(
        'SELECT name FROM sqlite_master WHERE type="table"'
    ).fetchall()
    for table_name in tables: #('wordmapping', 'docindraw', 'docindnorm'):
        table_name = table_name[0]
        if table_name != 'tfidfraw' and table_name != 'tfidfnorm':
            data = dct[table_name]
            statement = INSERT_STMT[table_name]
            cursor.executemany(
                statement, data
            )