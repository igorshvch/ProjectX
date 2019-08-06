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
    dirutil as dru,
)
from atctds_search_civil.textproc import rwtools
from atctds_search_civil.gsm_wrap import (
    pipeline_bgr, form_output, QueryProcessor
)

MESSAGES = {
    'start_mes': '>>> Здравствуйте! Вы начали новый сеанс!',
    'fm_dir': 'Выбрана папка с файлами: {}',
    'fm_file': 'Выбран файл: {}',
    'fm_error': 'ВНИМАНИЕ! Ошибка в указании пути',
    'fm_save': 'Выбрана папка для сохранения: {}',
    'corpus_proc': '>>> Индексирую корпус документов',
    'corpus_res': 'Корпус обработан. Документов всего: {}',
    'date_sel': 'Дата загрузки в СПС "КонсультантПлюс", начиная с которой будут подобраны судебные акты: {}',
    'date_error': 'Выбранная дата находится за пределами доступного диапазона. Последняя доступная дата: {}',
    'contents_proc': '>>> Загружаю оглавления ПСП',
    'contents_total': 'Всего кирпичей (выводов или позиций) в текущей версии оглавлений ПСП: {}',
    'concls_load': 'Загружено выводов: {}',
    'concls_found': 'Найдено кирпичей (выводов или позиций) в текущей версии оглавлений ПСП: {}',
    'anlz_start': '>>> Обрабатываю корпус документов',
    'anlz_first_step': '>>> Ищу похожие документы',
    'anlz_end': 'Анализ документов закончен, результаты записаны в папку {}',
    'new_session': '>>> Вы начали новый сеанс!',
}

INTERNAL_PATHS = {
    'contents': pthl.Path().home().joinpath(
        'Робот', '_Работа программы', 'Оглавление ПСП'
    ),
    'stpw': pthl.Path().home().joinpath(
        'Робот', '_Работа программы', 'Стоп-слова', 'custom_stpw_wo_objections'
    ),
    'res': pthl.Path().home().joinpath(
        'Робот', '03 Результаты'
    ),
    'icon': lambda: pthl.Path(__file__).parent.joinpath('data/pad_icon2.ico'),
}

LOCK = thrd.Lock()


class MainLogic(smg.MainFrame):
    def __init__(self, parent):
        parent.title('Автоматический добор судебной практики для ПСП')
        parent.iconbitmap(INTERNAL_PATHS['icon']())
        smg.MainFrame.__init__(
            self,
            parent,
            icon_path=INTERNAL_PATHS['icon']()
        )
        self.corpus_iterator = None
        self.concls = None
        self.date = None
        self.max_date = None
        self.paths_to_corpus_and_concls = {key:None for key in ('CD', 'CNL')}
        self.save_res_folder = None
        self.start_widget()
        self.buttons_to_actions()
        self.print_in(MESSAGES['start_mes'])
        self.check_start_button_state()
        self.check_new_session_button_state()
    
    def print_in(self, text):
        self.widgets['TextArea'].btn_clean_all['state'] = 'normal'
        self.widgets['TextArea'].print_in(dbg.messanger(text))
    
    def switch_clean_buttons(self, state):
        if state != 'normal' and state != 'disabled':
            raise ValueError('Incorrect argument: {}'.format(state))
        btns = (
            self.widgets['FileManager'].btn_clean_all,
            self.widgets['FileManager'].btn_clean_CD,
            self.widgets['FileManager'].btn_clean_CNL,
            self.widgets['FileManager'].btn_clean_Save,
            self.widgets['ListView'].btn_clean_all,
            self.widgets['DateBox'].btn_clean_all,
            self.widgets['TextArea'].btn_clean_all
        )
        for btn in btns:
            btn['state'] = state

    def check_start_button_state(self):
        if self.concls and self.corpus_iterator and self.date:
            self.widgets['ControlButtons'].btn_Start['state'] = 'normal'
        else:
            self.widgets['ControlButtons'].btn_Start['state'] = 'disabled'
        self.after(100, self.check_start_button_state)
    
    def check_new_session_button_state(self):
        if (
            self.paths_to_corpus_and_concls['CD']
            or self.paths_to_corpus_and_concls['CNL']
            or self.save_res_folder
        ):
            self.widgets['ControlButtons'].btn_clean_all['state'] = 'normal'
        else:
            self.widgets['ControlButtons'].btn_clean_all['state'] = 'disabled'
        self.after(100, self.check_new_session_button_state)
                
    def fill_in_DateBox_with_actual_years(self):
        min_year = self.corpus_iterator.dates_range[0].year
        self.max_date = self.corpus_iterator.dates_range[1]
        for cmb in (
            self.widgets['DateBox'].cmb_Year,
            self.widgets['DateBox'].cmb_Month
        ):
            cmb['state'] = 'readonly'
        self.widgets['DateBox'].cmb_Year['values'] = [
            str(year) for year in range(min_year, self.max_date.year+1, 1)
        ]


#################Start of subthreads or subprocesses part:
    @dbg.method_speaker_timer('Corpus evaluation!')
    def process_corpus(self, folder_path):
        self.widgets['TextArea'].prog_bar.start()
        with LOCK:
            self.print_in(MESSAGES['corpus_proc'])
        self.widgets['FileManager'].btn_clean_CD['state'] = 'disabled'
        self.widgets['FileManager'].btn_clean_all['state'] = 'disabled'
        self.widgets['FileManager'].btn_CNL['state'] = 'disabled'
        self.widgets['FileManager'].btn_clean_all['state'] = 'disabled'
        self.corpus_iterator = iot.TextInfoCollectorEndDate(folder_path)
        self.corpus_iterator.process_files()
        corp_len = len(self.corpus_iterator)
        with LOCK:
            self.print_in(MESSAGES['corpus_res'].format(corp_len))
        self.widgets['FileManager'].btn_clean_CD['state'] = 'normal'
        self.widgets['FileManager'].btn_clean_all['state'] = 'normal'
        self.widgets['FileManager'].btn_CNL['state'] = 'normal'
        self.widgets['FileManager'].btn_clean_all['state'] = 'normal'
        self.fill_in_DateBox_with_actual_years()
        self.widgets['TextArea'].prog_bar.stop()
    
    @dbg.method_speaker_timer('Conclusions evaluation!')
    def process_concls(self, file_path):
        self.widgets['TextArea'].prog_bar.start()
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
        self.widgets['TextArea'].prog_bar.stop()
    
    @dbg.method_speaker_timer('Start gensim pipeline!')
    def start_pipline(self, corpus_iterator, concls, date, save_res_folder):
        self.widgets['TextArea'].prog_bar.start()
        self.switch_clean_buttons('disabled')
        stpw = rwtools.load_pickle(INTERNAL_PATHS['stpw'])
        current_save_folder = dru.create_save_folder(
            save_res_folder, dbg.strftime('%Y-%m-%d %H-%M')
        )
        with LOCK:
            self.print_in(MESSAGES['anlz_first_step'])
        current_corpus_iterator = corpus_iterator.find_docs_after_date(date)
        new_corpus_iterator, dct, dct_tfidf, sim_obj = pipeline_bgr(
            current_corpus_iterator, stpw, 10, 0.925, num_best=15
        )
        for ind, concl in enumerate(concls, start=1):
            holder = []
            print(concl)
            query = QueryProcessor(concl, stpw)
            res = form_output(
                new_corpus_iterator, dct, dct_tfidf, sim_obj, query
            )
            for item in res:
                print('\t\t', *item)
            holder.append(concl)
            holder.extend([item[0] for item in res])
            res_string = '\n'.join(holder)
            file_name = 'Вывод {:0>3d}.txt'.format(ind)
            with open(current_save_folder.joinpath(file_name), mode='w') as f:
                f.write(res_string)            
        self.switch_clean_buttons('normal')
        self.widgets['TextArea'].prog_bar.stop()
#################End of subthreads or subprocesses part


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
            self.paths_to_corpus_and_concls[widget_var] = path
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
        self.concls = None
    
    @dbg.method_speaker('Catch DateBox cmb_Day selection!')
    def retrieve_date(self):
        self.widgets['DateBox'].process_day(None) #None is a filler for tk.event argument holder in datebox.py DateBox method
        date = self.widgets['DateBox'].extract_internal_data()
        if date > self.max_date:
            self.print_in(MESSAGES['date_error'].format(self.max_date))
            return None
        self.print_in(MESSAGES['date_sel'].format(date))
        self.date = date
    
    @dbg.method_speaker('Catch ControlButtons.btn_Start press!')
    def start_analyzis(self):
        self.print_in(MESSAGES['anlz_start'])
        corpus_iterator = self.corpus_iterator
        concls = self.concls
        date = self.date
        save_res_folder = self.save_res_folder
        self.corpus_iterator = None
        self.concls = None
        self.date = None
        worker = thrd.Thread(
            target=self.start_pipline,
            args=(corpus_iterator, concls, date, save_res_folder)
        )
        worker.start()
    
    @dbg.method_speaker('Catch ControlButtons.btn_clean_all press!')
    def clean_everything(self):
        self.clean_DateBox_and_ListView_when_reset_path_to_CD('clean_all')
        self.widgets['TextArea'].cmd_clean_all()
        self.widgets['ControlButtons'].cmd_clean_all()
        self.corpus_iterator = None
        self.concls = None
        self.date = None
        self.paths_to_corpus_and_concls = {key:None for key in ('CD', 'CNL')}
        self.save_res_folder = None
        self.print_in(MESSAGES['new_session'])
    
    @dbg.method_speaker('Catch ListView.manual_interface.btn_OK press!')
    def get_concl_from_manual_input(self):
        if not self.concls:
            self.concls = []
        concl = self.widgets['ListView'].manual_interface.res_var.get()
        concl = concl.split(
            self.widgets['ListView'].sep
        )
        concl = cnl.cleaner_for_manually_entered_query(concl)
        if concl:
            self.concls.append(concl)
            self.widgets['ListView'].btn_clean_all['state'] = 'normal'
            self.widgets['FileManager'].btn_CNL['state'] = 'disabled'
        self.widgets['ListView'].l_count_var.set(str(len(self.concls)))
        self.widgets['ListView'].lstb_var.set(self.concls)
    
    @dbg.method_speaker('Catch ListView.btn_Manual press!')
    def insert_manually(self):
        self.widgets['ListView'].cmd_insert_manually(solo_mode=False)
        self.widgets['ListView'].manual_interface.btn_OK['command'] = (
            self.get_concl_from_manual_input
        )
        self.widgets['ListView'].manual_interface.grid(
            column=0, row=0, sticky='nswe'
        )

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
        self.widgets['FileManager'].btn_clean_CNL['command'] = (
            self.clean_ListView_and_FileManager_CNL
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
            lambda x: self.retrieve_date()
        )
        self.widgets['ListView'].btn_clean_all['command'] = (
            self.clean_ListView_and_FileManager_CNL
        )
        self.widgets['ControlButtons'].btn_Start['command'] = (
            self.start_analyzis
        )
        self.widgets['ControlButtons'].btn_clean_all['command'] = (
            self.clean_everything
        )
        self.widgets['ListView'].btn_Manual['command'] = (
            self.insert_manually
        )


if __name__ == '__main__':
    ml = MainLogic(smg.tk.Tk())
    ml.start_widget_solo()
        