

PATTERNS = (
'''[Нн]алог[а-я]*
[Ии]нспекци[а-я]*
[Вв]знос[а-я]*
[Фф]онд[а-я]*
на прибыль
на добавленную стоимость
на доходы физических лиц
\bНДС\b
\bНДФЛ\b
[Нн]алогов[а-я]* орган[а-я]*'''
)

class DataHolder():
    def __init__(self):
        self.path_to_document_files = None
        self.path_to_raw_concls_file = None
        self.path_to_additional_info = None
        self.path_to_stop_words = None
        self.current_concls_class = None #int
        self.date_of_receiving = None #it's a timedate.date instance
        #the following attribute should have following structure:
        # {'cnl': 'text', 'group': int, 'add_info': True, 'cnl+add_info': 'text'}
        self.path_to_result_folder = None
        self.conclusions_data = None
        #Probably the following attribute should present into the class:
        #self.path_to_iopickler_obj = None



