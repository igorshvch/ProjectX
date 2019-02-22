import re

PATTERN_DATE = '(?<=от )[0-9]{1,2} [а-я]+? [0-9]{4}'

PATTERN_NUM = '(?<=N )+'

def func(corpus_iterator, start, holder):
    for i in range(start, len(corpus_iterator)):
        spl = corpus_iterator.find_doc(i).split('\n')
        req, case = spl[4][:-1], spl[6][:-1]
        if 'Дело' in case:
            item = req + ' ' + case
        else:
            item = req
        holder.append(item)
    return holder

def func2(holder):
    mapping = {
        'января':'01',
        'февраля':'02',
        'марта':'03',
        'апреля':'04',
        'мая':'05',
        'июня':'06',
        'июля':'07',
        'августа':'08',
        'сентября':'09',
        'октября':'10',
        'ноября':'11',
        'декабря':'12'
    }
    new_holder = []
    errors = []
    for ind, i in enumerate(holder):
        if 'N' in i:
            date, num = i.split(' N ')
            date = re.search(PATTERN_DATE, date).group()
            d, m, y = date.split(' ')
            m = mapping[m]
            date = '{}.{}.{}'.format(d,m,y)
            new_holder.append('{}\t{}\t{}'.format(date, num, i))
        else:
            errors.append(ind)
    return new_holder, errors

def func3(errors, corpus_iterator):
    holder = []
    for i in errors:
        head = corpus_iterator.find_doc(i).split('\n')[:10]
        head = [t.replace('\r', '') for t in head]
        holder.append(' ### '.join(head))
    return holder