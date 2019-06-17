import re

###Content=====================================================================
ARTICLE = r'Статья [0-9]{1,4}.*'
THEME = r'[0-9]{1,3}.*'
QUESTION = r'\t[0-9]{1,3}.*'
POSITION = r'\t\tПозиция.*'

STRIP = '1234567890 !"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~\t\n\r'

CONTENTS = {  
    '1': 'ВОУ',
    '2': 'Факторинг',
    '3': 'Агентирование',
    '4': 'Хранение. Общие положения',
    '6': 'Подряд общие положения',
    '7': 'КП общие положения',
    '8': 'РКП',
    '9': 'Поставка',
    '10': 'Заем',
    '11': 'Кредит',
    '12': 'ТКК',
    '13': 'Хранение на товарном складе',
    '14': 'Аренда общие положения',
    '15': 'Поручение',
    '16': 'Комиссия',
    '17': 'АЗС',
    '34': 'Доверительное управление имуществом',
    '36': 'АТС',
    '38': 'Банковский счет',
    '40': 'Расчеты',
    '42': 'Банковский вклад',
    '44': 'КПН'
}

CLEANED_ARTICLE_n_THEME= r'(?<=\. ).*'

#CLEANED_QUESTION_POS_1 = (
#    r'(?<=По вопросу ).*(?=у судов нет единой позиции|'
#    + r'существует две позиции|существует три позиции|'
#    + r'существует четыре позиции|существует пять позиций|'
#    + r'существуют две позиции|существуют три позиции|'
#    + r'существуют четыре позиции|существуют пять позиций)'
#)

#CLEANED_QUESTION_POS_2 = r'(?<=Вопрос ).*(?=решается судами по-разному)'

CLEANED_QUESTION_POS = {
    '0main': (
        r'(?<=По вопросу ).*(?=у судов нет единой позиции|'
        + r'существует две позиции|существует три позиции|'
        + r'существует четыре позиции|существует пять позиций|'
        + r'существуют две позиции|существуют три позиции|'
        + r'существуют четыре позиции|существуют пять позиций)'
    ),
    'dev1': r'(?<=Вопрос ).*(?=решается судами по-разному)',
    'dev2': r'.+(?=оценивается судами по-разному\Z)',
    'dev3': r'(?<=Единого подхода относительно ).*(?=в судебной практике нет)',
    'dev4': r'(?<=В судебной практике нет единого подхода по вопросу ).*',
    'dev5': r'(?<=По вопросу).*(?=позиции судов различны)',
    'dev6': r'(?<=По вопросу ).*(?=имеется две позиции)',
    'dev7': r'(?<=В отношении ).*(?=существует две позиции)',
    'dev8': r'(?<=Вывод из судебной практики).*'
}

CLEANED_POSITION = r'(?<=Позиция ).*'

#__CLEANED_QUESTION = r'(?<=Вывод из судебной практики: ).*'

def clean_question(text):
    for key in sorted(CLEANED_QUESTION_POS.keys()):
        if re.search(CLEANED_QUESTION_POS[key], text):
            question = re.search(CLEANED_QUESTION_POS[key], text).group()
            return question.strip(STRIP)
    return text.strip(STRIP)

def process_exist_contents(text, full_output=False):
    spl = text.rstrip('\n\t\r').split('\n')
    questions = []
    current_question = None
    questions_with_pos = []
    errors = []
    for ind, line in enumerate(spl):
        if re.match(ARTICLE, line):
            current_article = re.match(ARTICLE, line).group()
        elif re.match(THEME, line):
            current_theme = current_article, re.match(THEME, line).group()
        elif re.match(QUESTION, line):
            questions.append(
                (ind, *current_theme, re.match(QUESTION, line).group())
            ) # (IND, cur_art, cur_them, quest)
            current_question = None
        elif re.match(POSITION, line):
            if current_question:
                questions_with_pos.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                ) # (IND, cur_art, cur_them, quest, pos)
            else:
                current_question = questions.pop()[1:]
                questions_with_pos.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                ) # (IND, cur_art, cur_them, quest, pos)
        else:
            errors.append((ind, line))
        res = sorted(questions + questions_with_pos, key = lambda x: x[0])
        res = [[*item[1:]] for item in res]
    if full_output:
        return res, questions, questions_with_pos, errors
    else:
        return res

def clean_contents_questions(questions):
    results = []
    errors = []
    er_codes = 'art', 'them', 'quest'
    for q in questions:
        ind, article, theme, question = q
        try:
            article = re.search(CLEANED_ARTICLE_n_THEME, article).group()
            article = article.strip(STRIP)
        except:
            errors.append((ind, er_codes[0], article))
        try:
            theme = re.search(CLEANED_ARTICLE_n_THEME, theme).group()
            theme = theme.strip(STRIP)
        except:
            errors.append((ind, er_codes[1], theme))
        question = question.strip(STRIP)
        results.append((ind, article, theme, question))
    return results, errors

def clean_contents_questions_with_pos(questions_with_pos):
    results = []
    errors = []
    er_codes = 'art', 'them', 'quest', 'pos'
    for q in questions_with_pos:
        ind, article, theme, question, position = q
        try:
            article = re.search(CLEANED_ARTICLE_n_THEME, article).group()
            article = article.strip(STRIP)
        except:
            errors.append((ind, er_codes[0], article))
        try:
            theme = re.search(CLEANED_ARTICLE_n_THEME, theme).group()
            theme = theme.strip(STRIP)
        except:
            errors.append((ind, er_codes[1], theme))
        question = clean_question(question)
        try:
            position = re.search(CLEANED_POSITION, position).group()
            position = position.strip(STRIP)
        except:
            errors.append((ind, er_codes[3], position))
        results.append((ind, article, theme, question, position))
    return results, errors  

def join_contents_quest_and_poses(questions, questions_with_pos):
    joined = questions + questions_with_pos
    return sorted(joined, key = lambda x: x[0])

class ErrorsHandler():
    def __init__(self):
        self.errors_in_contents = {}
        self.errors_in_questions = {}
        self.errors_in_positions = {}
    
    def process_contents_files(self, file_paths_iterable):
        for fp in file_paths_iterable:
            doc_idn = fp.stem[:3].lstrip('0') #pathlib usage is implied
            with open(fp, mode='r') as f:
                text = f.read()
            _, q, p, er = process_exist_contents(text, full_output=True)
            if er:
                self.errors_in_contents[doc_idn] = er
                print(
                    'Index Errors caught in file id'
                    '{: >2s}. Total: {}'.format(doc_idn, len(er))
                )
            _, er_q = clean_contents_questions(q)
            if er_q:
                self.errors_in_questions[doc_idn] = er_q
                print(
                    'Questions Errors caught in file id',
                    '{: >2s}. Total: {}'.format(doc_idn, len(er_q))
                )
            _, er_p = clean_contents_questions_with_pos(p)
            if er_p:
                self.errors_in_positions[doc_idn] = er_p
                print(
                    'Positional Errors caught in file id',
                    '{: >2s}. Total: {}'.format(doc_idn, len(er_p))
                )
    
    def show_errors(self, mode='cnt'):
        modes = {
            'cnt' : self.errors_in_contents,
            'quest' : self.errors_in_questions,
            'pos' : self.errors_in_positions
        }
        for key in modes[mode]:
            print('Doc ID: {: >5s}'.format(key))
            for error in modes[mode][key]:
                print('\t', error)


def add_zeroes_or_increment(string):
    '''
    Take string and append two zeroes to it .
    If two zeroes are already at the end of the string
    increment numerical string ending by one:
    'somestring00' -> 'somestring01'
    '''
    ending = string[-2:]
    if ending.isdigit():
        if ending == '99':
            raise ValueError(
                'string ending has already reached maximum possible value'
                )
        num = int(ending)
        incremented_ending = '{:0>2d}'.format(num+1)
        return string[:-2] + incremented_ending
    else:
        return string+'00'


class ContentsBox():
    def __init__(self, idn, contents_list):
        self.contents_list = contents_list
        self.idn = idn
        self.__process()
    
    def __getitem__(self, index):
        '''
        Retrun element by absolute index created by process_exist_contents()
        '''
        if index in self.store_abs_ind:
            return self.store_abs_ind[index]
        else:
            raise IndexError('index out of range')
    
    def __len__(self):
        return len(self.contents_list)
    
    def __process(self):
        store_quest = {}
        store_abs_ind = {}
        for item in self.contents_list: #item: (IND, art, them, quest, [pos])
            ind = item[0]
            key = item[3].lower().replace(' ', '')
            key = add_zeroes_or_increment(key)
            if key in store_quest:
                key = add_zeroes_or_increment(key)
                store_quest[key] = item
            else:
                store_quest[key] = item
            #Some error hides here.
            #Before adding key incrementation similar 'keys' rewrote each other:
            #len(cbc.store['6'].store_abs_ind) => 478
            #len(cbc.store['6'].store_quest) => 422
            #After adding key incrementation some dicitionary items
            #are still missed:
            #len(cbc2.store['6'].store_abs_ind) => 478
            #len(cbc2.store['6'].store_quest) => 473
            store_abs_ind[ind] = item
        self.store_quest = store_quest
        self.store_abs_ind = store_abs_ind
    
    def find_by_quest(self, quest, verbose=False): #, testmode=False):
        norm_string = clean_question(quest)
        norm_string = norm_string.lower().replace(' ', '')
        norm_string = add_zeroes_or_increment(norm_string)
        if norm_string in self.store_quest:
            if verbose:
                print(
                    'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
                    +' >>> Exact match!'
                )
            #res = []
            while norm_string in self.store_quest:
                yield self.store_quest[norm_string]
                norm_string = add_zeroes_or_increment(norm_string)
                #res.append(self.store_quest[norm_string])
                #norm_string = add_zeroes_or_increment(norm_string)
            #return res
        #else:
        #    if testmode:
        #        if verbose:
        #            print(
        #                'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
        #                +' >>> No exact match. Trying to find most close result'
        #            )
        #        for key in self.store_quest:
        #            if norm_string in key:
        #                return self.store_quest[norm_string]
        #        if verbose:
        #            print(
        #                'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
        #                +' >>> No matches!'
        #            )
        #       return None
        #    else:
        #        raise KeyError('Question is not stored!')

    def find_by_relevant_index(self, index):
        '''
        Return element from in-class content_list
        '''
        return self.contents_list[index]

class ContentsBoxCollector():
    def __init__(self, file_paths_iterable):
        self.store = {}
        self.__process(file_paths_iterable)
    
    def __getitem__(self, index):
        pass
    
    def __process(self, file_paths_iterable):
        for fp in file_paths_iterable:
            doc_idn = fp.stem[:3].lstrip('0') #pathlib usage is implied
            with open(fp, mode='r') as f:
                text = f.read()
            _, q, p, _ = process_exist_contents(text, full_output=True)
            res_q, _ = clean_contents_questions(q)
            res_p, _ = clean_contents_questions_with_pos(p)
            joined = join_contents_quest_and_poses(res_q, res_p)
            self.store[doc_idn] = ContentsBox(
                (doc_idn, CONTENTS[doc_idn]), joined
            )
    
    def find_by_quest(self, quest, verbose=False):
        #speaker = 'ContentsBoxCollector:'
        for key in sorted(self.store.keys()):
            yield from self.store[key].find_by_quest(quest, verbose=verbose)
            #res = self.store[key].find_by_quest(quest, verbose=verbose)
            #if res:
            #    print(speaker, 'match found!')
            #    print(speaker, key+',', CONTENTS[key])
            #    break
        #return res


class QuestCleaner():
    '''
    Translate questions with annotations in raw text format to dictionary:
    {
        quest1: [ann1, ann2, ann3,... annN],
        quest2: [ann1,...]
        ...
    }
    '''

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.data = None
        self._transform()
    
    def __iter__(self):
        if self.data:
            for key in self.data:
                yield key, self.data[key]
        else:
            raise StopIteration('Data attribute is empty!')

    
    def _transform(self):
        data = {}
        split_level_1 = self.raw_text.split('\n')
        for ind, question in enumerate(split_level_1):
            try:
                first_char = question[0]
                print(ind)
            except IndexError:
                print(ind, 'FAIL')
                continue
            if isinstance(first_char, int) or isinstance(first_char, str):
                split_level_2 = question.split('\t')
                if split_level_2[0] in data:
                    raise KeyError(
                        'Question ia alreqdy in the dictionary!', 
                        split_level_2[0]
                    )
                data[split_level_2[0]] = [
                    text for text in split_level_2[1:]
                    if re.subn(' [\n\t]', '' ,text)[0] 
                ]
            else:
                pass
        self.data = data
    
    def find_by_quest(self, quest):
        norm_string = quest #clean_question(quest)
        #norm_string = norm_string.lower().replace(' ', '')
        if norm_string in self.data:
            return self.data[norm_string]
        else:
            raise KeyError('Question is not stored!')


def make_easter_greate_again(QC, CBC):
    '''
    QC - QuestCleaner() instance
    CBC - ContentsBoxCollector() instance
    '''
    for item in QC:
        question, anns = item
        contents_gen = CBC.find_by_quest(question)
        for ind, contents_item in enumerate(contents_gen):
            listed_item = list(contents_item)
            listed_item.append(anns[ind])
            listed_item = [str(i) for i in listed_item]
            print(' >>> '.join(listed_item))
            print('\n')