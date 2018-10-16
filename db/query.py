import re
from time import time

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

def load_mapping(connection):
    cursor = connection.cursor()
    mapping = cursor.execute(
        '''
        SELECT raww, norm FROM wordmapping
        '''
    ).fetchall()
    return {raww:word for raww,word in mapping}

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

def load_all_postinglists(connection, mode='raw'):
    cursor = connection.cursor()
    if mode == 'raw':
        table = 'docindraw'
    elif mode == 'norm':
        table = 'docindnorm'
    docfreq = cursor.execute(
        '''
        SELECT word, postinglist FROM {}
        '''.format(table)
    ).fetchall()
    return {word:postlist.split(',') for word,postlist in docfreq}

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

def load_doc_vector(connection, act_id, mode='raw'):
    cursor = connection.cursor()
    if mode == 'raw':
        table='tfidfraw'
    elif mode == 'norm':
        table='tfidfnorm'
    vector = cursor.execute(
        '''
        SELECT vector FROM {}
        WHERE rowid=?
        '''.format(table),
        str(act_id)
    ).fetchone()[0]
    return vector

def iterate_row_loading(connection, table, cols, step=100):
    cursor = connection.cursor()
    total_rows = cursor.execute(
        "SELECT Count(*) FROM {}".format(table)
    ).fetchone()[0]
    cols = ','.join(cols)
    iterations = (
        total_rows//step+1 if total_rows % step != 0 else total_rows/step
    )
    for i in range(iterations):
        stmt = (
            '''
            SELECT ({cols}) FROM {tb}
            LIMIT {batch} OFFSET {ofs}
            '''.format(cols=cols, tb=table, batch=step, ofs=(i*step))
        )
        yield cursor.execute(stmt).fetchall()

def overlap_score_measure(connection, query_text, mode='raw', step=100):
    if mode == 'raw':
        table='tfidfraw'
    elif mode == 'norm':
        table='tfidfnorm'
    query_text = re.split(r'\W', query_text.lower(), flags=re.DOTALL)
    vocab = {
        word:position for position,word
        in enumerate(load_all_words(connection, words=mode))
    }
    positions = [vocab[word] for word in query_text if word in vocab]
    gen = iterate_row_loading(connection, table, ('vector',), step=step)
    holder = []
    inner_ind = 0
    local_timer = time()
    for ind, batch in enumerate(gen, start=1):
        local_time = time() - local_timer
        print(
            'Batch # {: >3d}'.format(ind),
            'TIME: {: >6.3f}m, {: >8.3f}s'.format(local_time/60, local_time)
        )
        for inner_ind, row in enumerate(batch, start=inner_ind):
            vector = row[0].split(',')
            vector = [float(coord) for coord in vector]
            holder.append((inner_ind, sum(vector[pos] for pos in positions)))
    return holder

def overlap_score_measure_old(connection, query_text, mode='raw'):
    cursor = connection.cursor()
    if mode == 'raw':
        table='tfidfraw'
    elif mode == 'norm':
        table='tfidfnorm'
    query_text = re.split(r'\W', query_text.lower(), flags=re.DOTALL)
    N = cursor.execute("SELECT Count(*) FROM acts").fetchone()[0]
    vocab = {
        word:position for position,word
        in enumerate(load_all_words(connection, words=mode))
    }
    positions = [vocab[word] for word in query_text if word]
    stmt = (
        '''
        SELECT vector FROM {}
        WHERE rowid=?
        '''.format(table)
    )
    gen = ((stmt, str(i)) for i in range(1, N+1))
    holder = []
    local_timer = time()
    for ind, vals in enumerate(gen, start=1):
        vector = cursor.execute(vals[0], (vals[1],)).fetchone()[0]
        vector = vector.split(',')
        vector = [float(coord) for coord in vector]
        holder.append((ind, sum(vector[j] for j in positions)))
        if ind % 100 == 0:
            local_time = time() - local_timer
            print(
                'Act #',
                ind,
                'TIME: {:.3f}m, {:.3f}s'.format(local_time/60, local_time)
            )
    return holder


##########
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
    