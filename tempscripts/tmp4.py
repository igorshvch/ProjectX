#prototype of class for question parsing:
#7.4. Вывод из судебной практики: По вопросу о том, обязан ли покупатель оплатить полученный товар, если продавец не предоставил счета-фактуры, существует две позиции судов	Отсутствие у покупателя счетов-фактур не освобождает последнего от обязанности оплаты фактически полученного товара	Правомерно неисполнение обязанности по оплате полученного товара до представления оригинала счета - фактуры		
#5.2. Вывод из судебной практики: По вопросу о возможности применения норм Гражданского кодекса РФ об аренде к договору, по которому за плату предоставляется во временное владение и пользование место для установки и эксплуатации рекламной конструкции, существует две позиции судов	Договор на установку и эксплуатацию рекламной конструкции подразумевает обеспечение арендодателем временного использования арендатором объекта недвижимости (размещение рекламной конструкции) за плату. Подобные условия соответствуют определению договора аренды.	ДОБОР НЕ НУЖЕН		

import re

class QuestCleaner():
    '''
    Translate questions with annotations in raw text format to dictionary:
    {
        quest1: [ann1, ann2, ann3,... annN],
        quest2: [ann1,...]
        ...
    }
    '''

    def __init__(self, file):
        self.raw_text = file.read()
        self.data = None
    
    def transform(self):
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
                data[split_level_2[0]] = [ #production: clean_question(split_level_2[0])
                    text for text in split_level_2[1:]
                    if re.subn(' [\n\t]', '' ,text)[0] 
                ]
            else:
                pass
        self.data = data
        