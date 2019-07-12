#import multiprocessing as mpc
import threading as thrd
import time
from tkinter import filedialog as fd
import pathlib as pthl

from atctds_search_civil import (
    simplegui as smg,
    debugger as dbg,
    iotext as iot,
    cnl_civil as cnl,
)
from atctds_search_civil.textproc import rwtools

MESSAGES = {
    'fm_dir': 'Выбрана папка с файлами: {}',
    'fm_file': 'Выбран файл: {}',
    'fm_error': 'ВНИМАНИЕ! Ошибка в указании пути',
    'fm_save': 'Выбрана папка для сохранения: {}',
    'corpus_proc': '>>> Обрабатываю корпус документов',
    'corpus_res': 'Корпус обработан. Документов всего: {}',
    'sel_date': 'Дата загрузки в СПС "КонсультантПлюс", начиная с которой будут подобраны судебные акты: {}',
    'contents_proc': '>>> Загружаю оглавления ПСП',
    'contents_total': 'Всего кирпичей (выводов или позиций) в ткущей версии оглавлений ПСП: {}',
    'concls_load': 'Загружено выводов: {}',
    'concls_found': 'Найдено кирпичей (выводов или позиций) в ткущей версии оглавлений ПСП: {}',
}

INTERNAL_PATHS = {
    'contents': pthl.Path().home().joinpath(
        'Робот', '_Работа программы', 'Оглавление ПСП'
    ),
}

LOCK = thrd.Lock()


class MainLogic(smg.MainFrame):
    def __init__(self, parent):
        smg.MainFrame.__init__(self, parent)
        self.corpus_iterator = None
        self.concls = None
        self.save_res_folder = None
        self.start_widget()
        self.buttons_to_actions()
    
    def print_in(self, text):
        self.widgets['TextArea'].btn_clean_all['state'] = 'normal'
        self.widgets['TextArea'].print_in(dbg.messanger(text))
    
    def fill_in_DateBox_with_actual_years(self):
        min_year = self.corpus_iterator.dates_range[0].year
        max_year = self.corpus_iterator.dates_range[1].year
        for cmb in (
            self.widgets['DateBox'].cmb_Year,
            self.widgets['DateBox'].cmb_Month
        ):
            cmb['state'] = 'readonly'
        self.widgets['DateBox'].cmb_Year['values'] = [
            str(year) for year in range(min_year, max_year+1, 1)
        ]

    @dbg.method_speaker_timer('Corpus evaluation!')
    def process_corpus(self, folder_path):
        with LOCK:
            self.print_in(MESSAGES['corpus_proc'])
        self.widgets['FileManager'].btn_clean_CD['state'] = 'disabled'
        self.widgets['FileManager'].btn_clean_all['state'] = 'disabled'
        self.corpus_iterator = iot.TextInfoCollector(folder_path)
        self.corpus_iterator.process_files()
        corp_len = len(self.corpus_iterator)
        with LOCK:
            self.print_in(MESSAGES['corpus_res'].format(corp_len))
        self.widgets['FileManager'].btn_clean_CD['state'] = 'normal'
        self.widgets['FileManager'].btn_clean_all['state'] = 'normal'
        self.fill_in_DateBox_with_actual_years()
    
    @dbg.method_speaker_timer('Conclusions evaluation!')
    def process_concls(self, file_path):
        with LOCK:
            self.print_in(MESSAGES['contents_proc'])
        iterable_paths = rwtools.collect_exist_files(
            INTERNAL_PATHS['contents'],
            suffix='.txt'
        )
        cbc = cnl.ContentsBoxCollector(iterable_paths)
        with open(file_path, mode='r') as f:
            raw_text = f.read()
        qc = cnl.QuestCleaner(raw_text)
        with LOCK:
            self.print_in(MESSAGES['contents_total'].format(len(cbc)))
            self.print_in(MESSAGES['concls_load'].format(len(qc)))
        self.concls = list(cnl.join_contents_and_questions(qc, cbc))
        with LOCK:
            self.print_in(MESSAGES['concls_found'].format(len(self.concls)))
        self.widgets['ListView'].l_count_var.set(str(len(self.concls)))
        self.widgets['ListView'].lstb_var.set(self.concls)
        self.widgets['ListView'].btn_clean_all['state'] = 'normal'
    
    @dbg.method_speaker('Catch FileManager.btn_CD or .btn_CNL press!')
    def filemanager_btn_CD_or_CNL_press(self, widget_var):
        optitons = {
            'CD': (
                self.widgets['FileManager'].cmd_CD,
                self.widgets['FileManager'].l_CD_var.get,
                'fm_dir',
                self.process_corpus
            ),
            'CNL': (
                self.widgets['FileManager'].cmd_CNL,
                self.widgets['FileManager'].l_CNL_var.get,
                'fm_file',
                self.process_concls
            )
        }
        cmd, tk_var_val_get, mes, func = optitons[widget_var]
        cmd()
        path = tk_var_val_get()
        if path:
            self.print_in(MESSAGES[mes].format(path))
            worker = thrd.Thread(target=func, args=(path,))
            worker.start()
        else:
            self.print_in(MESSAGES['fm_error'])

    @dbg.method_speaker('Catch FileManager.btn_Save press!')
    def store_save_path(self):
        self.widgets['FileManager'].cmd_Save()
        save_res_folder = self.widgets['FileManager'].l_Save_var.get()
        if save_res_folder:
            self.print_in(MESSAGES['fm_save'].format(save_res_folder))
            self.save_res_folder = save_res_folder
        else:
            self.print_in(MESSAGES['fm_error'])


#################legacy code starts:
    @dbg.method_speaker('Catch FileManager.btn_CNL press!')
    def index_text_files(self):
        self.widgets['FileManager'].cmd_CD()
        path = self.widgets['FileManager'].l_CD_var.get()
        if path:
            self.print_in(MESSAGES['fm_dir'].format(path))
            worker = thrd.Thread(target=self.process_corpus, args=(path,))
            worker.start()
        else:
            self.print_in(MESSAGES['fm_error'].format(path))
    
    @dbg.method_speaker('Catch FileManager.btn_CNL press!')
    def insert_processed_concls(self):
        self.widgets['FileManager'].cmd_CNL()
        path = self.widgets['FileManager'].l_CNL_var.get()
        if path:
            self.print_in(MESSAGES['fm_file'].format(path))
            worker = thrd.Thread(target=self.process_concls, args=(path,))
            worker.start()
        else:
            self.print_in(MESSAGES['fm_error'].format(path))
#################legacy code ends

    
    @dbg.method_speaker('Catch FileManager.btn_clean_CD or .btn_clean_all press!')
    def clean_DateBox_and_ListView_when_reset_path_to_CD(self, widget_var):
        options = {
            'clean_CD': (lambda: self.widgets['FileManager'].cmd_clean('CD'),),
            'clean_all': (
                self.widgets['FileManager'].cmd_clean_all,
                self.widgets['ListView'].cmd_clean_all
            )
        }
        for func in options[widget_var]:
            func()
        self.widgets['DateBox'].cmd_clean_all()
        self.widgets['DateBox'].cmb_Year['values'] = ''
        for cmb in (
            self.widgets['DateBox'].cmb_Year,
            self.widgets['DateBox'].cmb_Month,
            self.widgets['DateBox'].cmb_Day,
            self.widgets['DateBox'].btn_clean_all
        ):
            cmb['state'] = 'disabled'
    
    @dbg.method_speaker('Catch TextArea.btn_clean_all press!')
    def clean_TextArea(self):
        self.widgets['TextArea'].cmd_clean_all()
        self.widgets['TextArea'].btn_clean_all['state'] = 'disabled'
    
    @dbg.method_speaker('Catch ListView.btn_clean_all press!')
    def clean_ListView_and_FileManager_CNL(self):
        self.widgets['ListView'].cmd_clean_all()
        self.widgets['FileManager'].cmd_clean('CNL')

    @dbg.method_speaker('Changing buttons-to-actions mapping!')
    def buttons_to_actions(self):
        self.widgets['FileManager'].btn_CD['command'] = (
            lambda: self.filemanager_btn_CD_or_CNL_press('CD')
        )
        self.widgets['FileManager'].btn_CNL['command'] = (
            lambda: self.filemanager_btn_CD_or_CNL_press('CNL')
        )
        self.widgets['FileManager'].btn_Save['command'] = (
            self.store_save_path
        )
        self.widgets['FileManager'].btn_clean_CD['command'] = (
            lambda: (
                self.clean_DateBox_and_ListView_when_reset_path_to_CD(
                    'clean_CD'
                )
            )
        )
        self.widgets['FileManager'].btn_clean_all['command'] = (
            lambda: (
                self.clean_DateBox_and_ListView_when_reset_path_to_CD(
                    'clean_all'
                )
            )
        )
        self.widgets['TextArea'].btn_clean_all['command'] = (
            self.clean_TextArea
        )
        self.widgets['DateBox'].cmb_Day.bind(
            '<<ComboboxSelected>>',
            lambda x: (
                self.widgets['DateBox'].process_day(None), #None is a filler for tk.event argument holder in datebox.py DateBox method
                self.print_in(
                    MESSAGES['sel_date'].format(
                        self.widgets['DateBox'].extract_internal_data()
                    )
                )
            )
        )
        self.widgets['ListView'].btn_clean_all['command'] = (
            self.clean_ListView_and_FileManager_CNL
        )
    


if __name__ == '__main__':
    ml = MainLogic(smg.tk.Tk())
    ml.start_widget_solo()
        