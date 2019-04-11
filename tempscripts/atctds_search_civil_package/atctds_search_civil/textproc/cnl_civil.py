import re
from . import rwtools

###Content=====================================================================
ARTICLE = r'Статья [0-9]{1,4}.*'
THEME = r'[0-9]{1,3}.*'
QUESTION = r'\t[0-9]{1,3}.*'
POSITION = r'\t\tПозиция.*'

STRIP = '1234567890 !"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~\t\n\r'

CLEANED_ARTICLE_n_THEME= r'(?<=\. ).*'

__CLEANED_QUESTION = r'(?<=Вывод из судебной практики: ).*'

CLEANED_QUESTION_POS_1 = (
    r'(?<=По вопросу ).*(?=у судов нет единой позиции|существует две позиции|существует три позиции|существует четыре позиции|существует пять позиций|существуют две позиции|существуют три позиции|существуют четыре позиции|существуют пять позиций)'
)

CLEANED_QUESTION_POS_2 = r'(?<=Вопрос ).*(?=решается судами по-разному)'

CLEANED_POSITION = r'(?<=Позиция ).*'


def process_exist_index(text, full_output=False):
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

def clean_index_questions(questions):
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

def clean_index_questions_with_pos(questions):
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
        if re.search(CLEANED_QUESTION_POS_1, question):
            question = re.search(CLEANED_QUESTION_POS_1, question).group()
            question = question.strip(STRIP)
        elif re.search(CLEANED_QUESTION_POS_2, question):
            question = re.search(CLEANED_QUESTION_POS_2, question).group()
            question = question.strip(STRIP)
        else:
            errors.append((ind, er_codes[2], question))
        try:
            position = re.search(CLEANED_POSITION, position).group()
            position = position.strip(STRIP)
        except:
            errors.append((ind, er_codes[3], position))
        results.append((ind, article, theme, question, position))
    return results, errors  

def join_index_quest_and_poses(questions, positions):
    joined = questions + positions
    return sorted(joined, key = lambda x: x[0])

class ErrorsHandler():
    def __init__(self):
        self.errors_in_indices = {}
        self.errors_in_questions = {}
        self.errors_in_positions = {}
    
    def process_index_files(self, file_paths_iterable):
        for fp in file_paths_iterable:
            doc_index = fp.stem[:3].lstrip('0') #pathlib usage is implied
            with open(fp, mode='r') as f:
                text = f.read()
            _, q, p, er = process_exist_index(text, full_output=True)
            if er:
                self.errors_in_indices[doc_index] = er
                print(
                    'Index Errors catched in file id'
                    '{: >2s}. Total: {}'.format(doc_index, len(er))
                )
            res_q, er_q = clean_index_questions(q)
            if er_q:
                self.errors_in_questions[doc_index] = er_q
                print(
                    'Questions Errors catched in file id',
                    '{: >2s}. Total: {}'.format(doc_index, len(er_q))
                )
            res_p, er_p = clean_index_questions_with_pos(p)
            if er_p:
                self.errors_in_positions[doc_index] = er_p
                print(
                    'Positional Errors catched in file id',
                    '{: >2s}. Total: {}'.format(doc_index, len(er_p))
                )
    
    def show_errors(self, mode='ind'):
        modes = {
            'ind' : self.errors_in_indices,
            'quest' : self.errors_in_questions,
            'pos' : self.errors_in_positions
        }
        for key in modes[mode]:
            print('Doc ID: {: >5s}'.format(key))
            for error in modes[mode][key]:
                print('\t', error)
            

class IndexBox():
    def __init__(self, index_list):
        self.index_list = index_list
        self.__processed()
    
    def __getitem__(self, index):
        return self.index_list[index]
    
    def __len__(self):
        return len(self.index_list)
    
    def __processed(self):
        store_quest = {}
        store_abs_ind = {}
        for item in self.index_list: #item: (IND, art, them, quest, [pos])
            ind = item[0]
            key = item[3].lower().replace(' ', '')
            store_quest[key] = item
            store_abs_ind[ind] = item
        self.store_quest = store_quest
        self.store_abs_ind = store_abs_ind
    
    def find_by_quest(self, quest, verbose=False):
        norm_string = quest.strip(STRIP)
        norm_string = norm_string.lower().replace(' ', '')
        if norm_string in self.store_quest:
            if verbose:
                print('Exact match!')
            return self.store_quest[norm_string]
        else:
            if verbose:
                print('No exact match. Tring to find most close result')
            for key in self.store_quest:
                if norm_string in key:
                    return self.store_quest[norm_string]
            if verbose:
                print('No matches!')
            return None
    
    def find_by_index(self, index):
        if index in self.store_abs_ind:
            return self.store_abs_ind[index]
        else:
            raise IndexError('index out of range')
            
        