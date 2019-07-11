#import multiprocessing as mpc
import threading as thrd
import time
from tkinter import filedialog as fd

from atctds_search_civil import (
    simplegui as smg,
    debugger as dbg,
    iotext as iot,
)

MESSAGES = {
    'fm_dir_CD': 'Выбрана папка с файлами, содержащими суденбыне акты: {}',
    'fm_error': 'ВНИМАНИЕ! Ошибка в указании пути',
    'proc_corp': 'Корпус обработан. Документов всего: {}',
    'sel_date': 'Дата загрузки в СПС "КонсультантПлюс", начиная с которой будут подобраны судебные акты: {}'
}

LOCK = thrd.Lock()


class MainLogic(smg.MainFrame):
    def __init__(self, parent):
        smg.MainFrame.__init__(self, parent)
        self.corpus_iterator = None
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
        self.widgets['FileManager'].btn_clean_CD['state'] = 'disabled'
        self.widgets['FileManager'].btn_clean_all['state'] = 'disabled'
        self.corpus_iterator = iot.TextInfoCollector(folder_path)
        self.corpus_iterator.process_files()
        corp_len = len(self.corpus_iterator)
        with LOCK:
            self.print_in(MESSAGES['proc_corp'].format(corp_len))
        self.widgets['FileManager'].btn_clean_CD['state'] = 'normal'
        self.widgets['FileManager'].btn_clean_all['state'] = 'normal'
        self.fill_in_DateBox_with_actual_years()
    
    @dbg.method_speaker('Catch FileManager.btn_CD press!')
    def index_text_files(self):
        self.widgets['FileManager'].cmd_CD()
        path = self.widgets['FileManager'].l_CD_var.get()
        if path:
            self.print_in(MESSAGES['fm_dir_CD'].format(path))
            worker = thrd.Thread(target=self.process_corpus, args=(path,))
            worker.start()
        else:
            self.print_in(MESSAGES['fm_error'].format(path))
    
    @dbg.method_speaker('Catch FileManager.btn_clean_CD or .btn_clean_all press!')
    def clean_when_reset_path_to_CD(self, widget_var):
        options = {
            'clean_CD': lambda: self.widgets['FileManager'].cmd_clean('CD'),
            'clean_all': self.widgets['FileManager'].cmd_clean_all
        }
        options[widget_var]()
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

    @dbg.method_speaker('Changing buttons-to-actions mapping!')
    def buttons_to_actions(self):
        self.widgets['FileManager'].btn_CD['command'] = self.index_text_files
        self.widgets['FileManager'].btn_clean_CD['command'] = (
            lambda: self.clean_when_reset_path_to_CD('clean_CD')
        )
        self.widgets['FileManager'].btn_clean_all['command'] = (
            lambda: self.clean_when_reset_path_to_CD('clean_all')
        )
        self.widgets['TextArea'].btn_clean_all['command'] = (
            self.clean_TextArea
        )
        self.widgets['DateBox'].cmb_Day.bind(
            '<<ComboboxSelected>>',
            lambda x: (
                self.widgets['DateBox'].process_day(x),
                self.print_in(
                    MESSAGES['sel_date'].format(
                        self.widgets['DateBox'].extract_internal_data()
                    )
                )
            )
        )
    


if __name__ == '__main__':
    ml = MainLogic(smg.tk.Tk())
    ml.start_widget_solo()
        