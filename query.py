import re

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