import re

def load_all_words(connection, words='raw'):
    cursor = connection.cursor()
    if words == 'raw':
        table = 'wordraw'
    elif words == 'norm':
        table = 'wordnorm'
    words = cursor.execute(
        '''
        SELECT word FROM {}
        '''.format(table)
    ).fetchall()
    return [row[0] for row in words]

def load_all_acts(connection):
    cursor = connection.cursor()
    acts = cursor.execute(
        '''
        SELECT act FROM acts
        '''
    ).fetchall()
    return [act[0] for act in acts]

def load_all_doc_freq(connection, mode='raw'):
    cursor = connection.cursor()
    if mode == 'raw':
        table = 'docindraw'
    elif mode == 'norm':
        table = 'docindnorm'
    docfreq = cursor.execute(
        '''
        SELECT word, docfreq FROM {}
        '''.format(table)
    ).fetchall()
    return {word:freq for word,freq in docfreq}

def tfidf_info(connection, act_id, word, mode='raw'):
    cursor = connection.cursor()
    N = cursor.execute("SELECT Count(*) FROM acts").fetchone()[0]
    #print('Total acts number: {}'.format(N))
    clean_word = word.lower()
    if mode == 'raw':
        table1 = 'docindraw'
        table2 = 'termfreqraw'
    elif mode == 'norm':
        table1 = 'docindnorm'
        table2 = 'termfreqnorm'
    df = cursor.execute(
        '''
        SELECT docfreq FROM {}
        WHERE word=?
        '''.format(table1),
        (clean_word,)
    ).fetchone()[0]
    tf = cursor.execute(
        '''
        SELECT termfreq FROM {}
        WHERE actid=? AND word=?
        '''.format(table2),
        (act_id, clean_word)
    ).fetchone()[0]
    return N, df, tf

def find_all_words_raw(connection, query):
    words = re.split(r'\W', query.lower(), flags=re.DOTALL)
    words = [word for word in words if word]
    cursor = connection.cursor()
    post_lists = []
    acts_list = []
    for word in words:
        pl = cursor.execute(
            '''
            SELECT postinglist FROM docindraw
            WHERE word=?
            ''',
            (word,)
        ).fetchone()[0]
        post_lists.append(set(pl.split(',')))
    res_pl = post_lists[0].intersection(*post_lists[1:])
    print('Resulting posting list:\n{}'.format(res_pl))
    for index in res_pl:
        act = cursor.execute(
            '''
            SELECT act FROM acts
            WHERE id=?
            ''',
            (str(int(index)+1),)
        ).fetchone()
        acts_list.append(act)
    return post_lists, acts_list

def find_all_words_norm(connection, query):
    words = re.split(r'\W', query.lower(), flags=re.DOTALL)
    words = [word for word in words if word]
    cursor = connection.cursor()
    norm_query = []
    post_lists = []
    acts_list = []
    for word in words:
        nw = cursor.execute(
            '''
            SELECT norm FROM wordmapping
            WHERE raww=?
            ''',
            (word,)
        ).fetchone()[0]
        norm_query.append(nw)
    print('Normed query:\n{}'.format(norm_query))
    for lem in norm_query:
        pl = cursor.execute(
            '''
            SELECT postinglist FROM docindnorm
            WHERE word=?
            ''',
            (lem,)
        ).fetchone()[0]
        post_lists.append(set(pl.split(',')))
    res_pl = post_lists[0].intersection(*post_lists[1:])
    print('Resulting posting list:\n{}'.format(res_pl))
    for index in res_pl:
        act = cursor.execute(
            '''
            SELECT act FROM acts
            WHERE id=?
            ''',
            (str(int(index)+1),)
        ).fetchone()
        acts_list.append(act)
    return post_lists, acts_list