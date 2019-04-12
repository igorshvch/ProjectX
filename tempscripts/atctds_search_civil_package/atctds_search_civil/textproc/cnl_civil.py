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

CLEANED_QUESTION_POS_1 = (
    r'(?<=По вопросу ).*(?=у судов нет единой позиции|'
    + r'существует две позиции|существует три позиции|'
    + r'существует четыре позиции|существует пять позиций|'
    + r'существуют две позиции|существуют три позиции|'
    + r'существуют четыре позиции|существуют пять позиций)'
)

CLEANED_QUESTION_POS_2 = r'(?<=Вопрос ).*(?=решается судами по-разному)'

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
    'dev7': r'(?<=В отношении ).*(?=существует две позиции)'
}

CLEANED_POSITION = r'(?<=Позиция ).*'

__CLEANED_QUESTION = r'(?<=Вывод из судебной практики: ).*'

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
    positions = []
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
                positions.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                ) # (IND, cur_art, cur_them, quest, pos)
            else:
                current_question = questions.pop()[1:]
                positions.append(
                    (ind, *current_question, re.match(POSITION, line).group())
                ) # (IND, cur_art, cur_them, quest, pos)
        else:
            errors.append((ind, line))
        res = sorted(questions + positions, key = lambda x: x[0])
        res = [[*item[1:]] for item in res]
    if full_output:
        return res, questions, positions, errors
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

def clean_contents_questions_with_pos(questions):
    results = []
    errors = []
    er_codes = 'art', 'them', 'quest', 'pos'
    for q in questions:
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

def join_contents_quest_and_poses(questions, positions):
    joined = questions + positions
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
                    'Index Errors catched in file id'
                    '{: >2s}. Total: {}'.format(doc_idn, len(er))
                )
            _, er_q = clean_contents_questions(q)
            if er_q:
                self.errors_in_questions[doc_idn] = er_q
                print(
                    'Questions Errors catched in file id',
                    '{: >2s}. Total: {}'.format(doc_idn, len(er_q))
                )
            _, er_p = clean_contents_questions_with_pos(p)
            if er_p:
                self.errors_in_positions[doc_idn] = er_p
                print(
                    'Positional Errors catched in file id',
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


class ContentsBox():
    def __init__(self, idn, contents_list):
        self.contents_list = contents_list
        self.idn = idn
        self.__process()
    
    def __getitem__(self, index):
        return self.contents_list[index]
    
    def __len__(self):
        return len(self.contents_list)
    
    def __process(self):
        store_quest = {}
        store_abs_ind = {}
        for item in self.contents_list: #item: (IND, art, them, quest, [pos])
            ind = item[0]
            key = item[3].lower().replace(' ', '')
            store_quest[key] = item
            store_abs_ind[ind] = item
        self.store_quest = store_quest
        self.store_abs_ind = store_abs_ind
    
    def find_by_quest(self, quest, verbose=False):
        norm_string = clean_question(quest)
        norm_string = norm_string.lower().replace(' ', '')
        if norm_string in self.store_quest:
            if verbose:
                print(
                    'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
                    +' >>> Exact match!'
                )
            return self.store_quest[norm_string]
        else:
            if verbose:
                print(
                    'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
                    +' >>> No exact match. Tring to find most close result'
                )
            for key in self.store_quest:
                if norm_string in key:
                    return self.store_quest[norm_string]
            if verbose:
                print(
                    'Dox ID: {: >2s}, {: <35s}'.format(self.idn[0], self.idn[1])
                    +' >>> No matches!'
                )
            return None
    
    def find_by_index(self, index):
        if index in self.store_abs_ind:
            return self.store_abs_ind[index]
        else:
            raise IndexError('index out of range')

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
        speaker = 'ContentsBoxCollector:'
        for key in sorted(self.store.keys()):
            res = self.store[key].find_by_quest(quest, verbose=verbose)
            if res:
                print(speaker, 'match found!')
                print(speaker, key+',', CONTENTS[key])
                break
        return res



            
        