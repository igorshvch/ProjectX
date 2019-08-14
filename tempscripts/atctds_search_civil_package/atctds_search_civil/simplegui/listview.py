import sys
import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from atctds_search_civil import debugger as dbg
from atctds_search_civil.simplegui.patterns import (
    CommonInterface, CustomTextWidgetRu
)

class ListView(ttk.Frame, CommonInterface):
    def __init__(self, parent, icon_path=None, sep=' / ', **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label_lstb = None #label
        self.btn_FromFile = None
        self.btn_Manual = None
        self.lstb = None #tk.Listbox
        self.scrl_y = None #ttk.Scrollbar
        self.scrl_x = None #ttk.Scrollbar
        self.btn_clean_all = None
        self.label_count1 = None #label with description of the following widget
        self.label_count2 = None #label to count quantity of loaded conclusions
        self.lstb_var = tk.StringVar()
        self.l_count_var = tk.StringVar()
        self.manual_interface = None
        self.icon_path = icon_path
        self.sep = sep
    
    @dbg.method_speaker('Open interface to insert conclusion manually')
    def cmd_insert_manually(self, solo_mode=True):
        win = tk.Toplevel()
        if self.icon_path:
            win.iconbitmap(self.icon_path)
        win.title('Введите поисковый запрос вручную')
        self.manual_interface = ConclsManualInputCTWR(
            win,
            sep=self.sep
        )
        self.manual_interface.start_widget()
        if solo_mode:
            self.manual_interface.grid(column=0, row=0, sticky='nswe')
    
    @dbg.method_speaker('Show full text of the query!')
    def pop_up_info(self, event):
        try:
            index = self.lstb.curselection()[0]
        except IndexError:
            return None
        #data = self.lstb_var.get()
        #data = [item.strip("(',')") for item in data.split(', ')][index]
        data = self.lstb.get(index)
        win = tk.Toplevel()
        if self.icon_path:
            win.iconbitmap(self.icon_path)
        win.title('Текст поискового запроса в формате программы')
        txt = CustomTextWidgetRu(win, label='', btn_clean_all=False)
        txt.start_widget()
        txt.inner_insert('1.0', data)
        txt.txt['state'] = 'disabled'
        txt.grid(column=0, row=0, sticky='nwse')
    
    @dbg.method_speaker('Cleaning ListView widgets!')
    def cmd_clean_all(self):
        self.lstb_var.set('')
        self.l_count_var.set('')
        self.btn_clean_all['state'] = 'disabled'

    def build_widgets(self):
        self.label_lstb = ttk.Label(
            self,
            text='Список кирпичей (выводов или позиций)',
            anchor='center',
            width=30,
            relief='flat'
        )
        self.btn_FromFile = ttk.Button(
            self,
            text='Из файла',
            width=25
        )
        self.btn_Manual = ttk.Button(
            self,
            text='Ввести вручную',
            command=self.cmd_insert_manually,
            width=25
        )
        self.lstb = tk.Listbox(
            self,
            listvariable=self.lstb_var,
            height=10,
            width=50,
            selectmode='browse'
        )
        self.lstb.bind('<Double-1>', self.pop_up_info)

        self.scrl_y = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.lstb.yview
        )
        self.lstb['yscrollcommand'] = self.scrl_y.set
        self.scrl_x = ttk.Scrollbar(
            self,
            orient='horizontal',
            command=self.lstb.xview
        )
        self.lstb['xscrollcommand'] = self.scrl_x.set

        self.btn_clean_all = ttk.Button(
            self,
            text='X',
            command=self.cmd_clean_all,
            width=2,
            state='disabled'
        )
        self.label_count1 = ttk.Label(
            self,
            text='Всего кирпичей: ',
            anchor='e',
        )
        self.label_count2 = ttk.Label(
            self,
            textvariable=self.l_count_var,
            anchor='e',
            width=4,
            relief='sunken'
        )
        self.widget_dict = {
            'lstb': self.lstb,
            'btn_clean_all': self.btn_clean_all
        }
    
    def grid_inner_widgets(self):
        self.label_lstb.grid(column=0, row=0, columnspan=3, sticky='we')
        #self.btn_FromFile.grid(column=0, row=1, columnspan=2, sticky='e')
        self.btn_Manual.grid(column=0, row=1, columnspan=3, sticky='we')
        self.lstb.grid(column=0, row=2, columnspan=3, sticky='we')
        self.scrl_y.grid(column=3, row=2, sticky='nws')
        self.scrl_x.grid(column=0, row=3, columnspan=3, sticky='enw')
        self.btn_clean_all.grid(column=0, row=4, sticky='w')
        self.label_count1.grid(column=1, row=4, sticky='e')
        self.label_count2.grid(column=2, row=4, sticky='e')
        self.columnconfigure(0, weight=1)


class ConclsManualInput(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.label_article = None
        self.label_theme = None
        self.label_concl = None
        self.label_pos = None
        self.label_anno = None
        self.txt_article = None
        self.txt_theme = None
        self.txt_concl = None
        self.txt_pos = None
        self.txt_anno = None
        self.scrl_y_art = None
        self.scrl_y_thm = None
        self.scrl_y_cnl = None
        self.scrl_y_pos = None
        self.scrl_y_ann = None
        self.label_info_header = None
        self.label_info_content = None
        self.l_info_var = tk.StringVar()
    
    def load_entered_text(self):
        widgets = (
            self.txt_article,
            self.txt_theme,
            self.txt_concl,
            self.txt_pos,
            self.txt_anno,
        )
        text = ''
        for widget in widgets:
            raw_text = widget.get('1.0', 'end-1c')
            raw_text = raw_text.strip()
            text += raw_text + (' / ') if raw_text else ''
        self.l_info_var.set(text)
        self.after(100, self.load_entered_text)
    
    def custom_binding(self):
        #Text 'Article' binding:
        self.txt_article.bind(
                '<Control-igrave>',
                lambda x: self.custom_insert(self.txt_article)
            )
        self.txt_article.bind(
                '<Control-ocircumflex>',
                lambda x: self.custom_selection(self.txt_article)
            )
        self.txt_article.bind(
                '<Control-ntilde>',
                lambda x: self.custom_copy(self.txt_article)
            )
        #Text 'Theme' binding:
        self.txt_theme.bind(
                '<Control-igrave>',
                lambda x: self.custom_insert(self.txt_theme)
            )
        self.txt_theme.bind(
                '<Control-ocircumflex>',
                lambda x: self.custom_selection(self.txt_theme)
            )
        self.txt_theme.bind(
                '<Control-ntilde>',
                lambda x: self.custom_copy(self.txt_theme)
            )
        #Text 'Concl' binding:
        self.txt_concl.bind(
                '<Control-igrave>',
                lambda x: self.custom_insert(self.txt_concl)
            )
        self.txt_concl.bind(
                '<Control-ocircumflex>',
                lambda x: self.custom_selection(self.txt_concl)
            )
        self.txt_concl.bind(
                '<Control-ntilde>',
                lambda x: self.custom_copy(self.txt_concl)
            )
        #Text 'Pos' binding:
        self.txt_pos.bind(
                '<Control-igrave>',
                lambda x: self.custom_insert(self.txt_pos)
            )
        self.txt_pos.bind(
                '<Control-ocircumflex>',
                lambda x: self.custom_selection(self.txt_pos)
            )
        self.txt_pos.bind(
                '<Control-ntilde>',
                lambda x: self.custom_copy(self.txt_pos)
            )
        #Text 'Anno' binding:
        self.txt_anno.bind(
                '<Control-igrave>',
                lambda x: self.custom_insert(self.txt_anno)
            )
        self.txt_anno.bind(
                '<Control-ocircumflex>',
                lambda x: self.custom_selection(self.txt_anno)
            )
        self.txt_anno.bind(
                '<Control-ntilde>',
                lambda x: self.custom_copy(self.txt_anno)
            )
    
    def custom_insert(self, widget): #'<Control-igrave>'
        try:
            widget.delete('sel.first', 'sel.last')
        except:
            pass
        widget.insert(
            index=tk.INSERT,
            chars=self.selection_get(selection="CLIPBOARD")
        )
    
    def custom_selection(self, widget): #'<Control-ocircumflex>'
        widget.tag_add(tk.SEL, '1.0', 'end')
    
    def custom_copy(self, widget): #'<Control-ntilde>'
        '''
        https://stackoverflow.com/questions/579687/how-do-i-copy-a-string-to-the-clipboard-on-windows-using-python
        '''
        try:
            text = widget.get('sel.first', 'sel.last')
        except:
            return None
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()


    def build_widgets(self):
        text_width = 70
        text_height = 5

        self.label_article = ttk.Label(
            self,
            text='Введите номер и заголовок статьи:'
        )
        self.label_theme = ttk.Label(
            self,
            text='Введите название раздела, в который помещен вывод:'
        )
        self.label_concl = ttk.Label(
            self,
            text='Введите вывод:'
        )
        self.label_pos = ttk.Label(
            self,
            text='Введите позицию (если есть):'
        )
        self.label_anno = ttk.Label(
            self,
            text='Введите аннотацию вывода или позиции (если есть):'
        )

        self.txt_article = tk.Text(
            self,
            width=text_width,
            height=text_height,
        )
        self.txt_theme = tk.Text(
            self,
            width=text_width,
            height=text_height,
        )
        self.txt_concl = tk.Text(
            self,
            width=text_width,
            height=text_height,
        )
        self.txt_pos = tk.Text(
            self,
            width=text_width,
            height=text_height,
        )
        self.txt_anno = tk.Text(
            self,
            width=text_width,
            height=text_height,
        )
        self.custom_binding()
        
        self.scrl_y_art = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt_article.yview
        )
        self.txt_article['yscrollcommand'] = self.scrl_y_art.set
        
        self.scrl_y_thm = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt_theme.yview
        )
        self.txt_theme['yscrollcommand'] = self.scrl_y_thm.set

        self.scrl_y_cnl = tk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt_concl.yview
        )
        self.txt_concl['yscrollcommand'] = self.scrl_y_cnl.set

        self.scrl_y_pos = tk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt_pos.yview
        )
        self.txt_pos['yscrollcommand'] = self.scrl_y_pos.set

        self.scrl_y_ann = tk.Scrollbar(
            self,
            orient='vertical',
            command=self.txt_anno.yview
        )
        self.txt_anno['yscrollcommand'] = self.scrl_y_ann.set

        self.label_info_header = ttk.Label(
            self,
            text='Текст запроса:'
        )
        self.label_info_content = ttk.Label(
            self,
            textvar=self.l_info_var,
            wraplength=550
        )

    def grid_inner_widgets(self):
        self.load_entered_text()
        labels_and_rows = (
            (self.label_article, 0),
            (self.label_theme, 2),
            (self.label_concl, 4),
            (self.label_pos, 6),
            (self.label_anno, 8)
        )
        for widget, row in labels_and_rows:
            widget.grid(column=0, row=row, sticky='nw')

        texts_scrollbars_and_rows = (
            (self.txt_article, self.scrl_y_art, 1),
            (self.txt_theme, self.scrl_y_thm, 3),
            (self.txt_concl, self.scrl_y_cnl, 5),
            (self.txt_pos, self.scrl_y_pos, 7),
            (self.txt_anno, self.scrl_y_ann, 9)
        )
        for widget_t, widget_s, row in texts_scrollbars_and_rows:
            widget_t.grid(column=0, row=row, pady=(0,10), sticky='nws')
            widget_s.grid(column=1, row=row, pady=(0,10), sticky='nws')
        
        self.label_info_header.grid(column=0, row=10, sticky='nw')
        self.label_info_content.grid(column=0, row=11, sticky='nw')


class ConclsManualInputCTWR(ttk.Frame, CommonInterface):
    def __init__(self, parent, sep=' / ', **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.sep = sep
        self.txt_article = None
        self.txt_theme = None
        self.txt_concl = None
        self.txt_pos = None
        self.txt_anno = None
        self.label_res = None
        self.btn_clean_all = None
        self.btn_OK = None
        self.inner_txt_widgets = None
        self.res_var = tk.StringVar()
    
    @dbg.method_speaker('Register btn_clean_all press!')
    def cmd_clean_all(self):
        for widget in self.inner_txt_widgets:
            widget.cmd_clean_all()
        self.res_var.set('')
    
    @dbg.method_speaker('Register btn_OK press!')
    def dummy_method(self):
        return None
    
    def build_widgets(self):
        text_width = 70
        text_height = 5
        self.txt_article = CustomTextWidgetRu(
            self,
            label='Введите номер и заголовок статьи:',
            t_width=text_width,
            t_height=text_height
        )
        self.txt_theme = CustomTextWidgetRu(
            self,
            label='Введите название раздела, в который помещен вывод:',
            t_width=text_width,
            t_height=text_height
        )
        self.txt_concl = CustomTextWidgetRu(
            self,
            label='Введите вывод:',
            t_width=text_width,
            t_height=text_height
        )
        self.txt_pos = CustomTextWidgetRu(
            self,
            label='Введите позицию (если есть):',
            t_width=text_width,
            t_height=text_height
        )
        self.txt_anno = CustomTextWidgetRu(
            self,
            label='Введите аннотацию вывода или позиции (если есть):',
            t_width=text_width,
            t_height=text_height
        )
        self.label_res = ttk.Label(
            self,
            textvar=self.res_var,
            wraplength=550
        )
        self.inner_txt_widgets = (
            self.txt_article,
            self.txt_theme,
            self.txt_concl,
            self.txt_pos,
            self.txt_anno,
        )
        #Btn:
        self.btn_clean_all = ttk.Button(
            self,
            text='Очистить все',
            command=self.cmd_clean_all
        )
        self.btn_OK = ttk.Button(
            self,
            text='Ок',
            command=self.dummy_method
        )
    
    def grid_inner_widgets(self):
        for ind, widget in enumerate(self.inner_txt_widgets):
            widget.start_widget()
            widget.grid(column=0, row=ind, columnspan=3, sticky='nw')
        self.btn_clean_all.grid(column=1, row=ind+1, sticky='ew')
        self.btn_OK.grid(column=2, row=ind+1, sticky='ew')
        self.label_res.grid(column=0, row=ind+2, columnspan=3, sticky='nw')
        self.load_entered_text()
    
    def load_entered_text(self):
        text = ''
        for widget in self.inner_txt_widgets:
            try:
                raw_text = widget.inner_get('1.0', 'end-1c')
            except:
                continue
            raw_text = raw_text.strip()
            if text:
                if raw_text:
                    text += self.sep + raw_text
            else:
                text = raw_text
        self.res_var.set(text)
        self.update()
        self.after(10, self.load_entered_text)


###############################################################################
############################### testing: ######################################
###############################################################################

from atctds_search_civil.testtools import rd, gts

class ListViewTest(ListView):
    def __init__(self, parent, **kwargs):
        ListView.__init__(self, parent, **kwargs)  

    @dbg.method_speaker('Inserting randomly generated data!')
    def insert_data(self):
        data = gts(rd.randint(3,20))
        count = str(len(data))
        self.lstb_var.set(data)
        self.l_count_var.set(count)
    
    @dbg.method_speaker('Deleting data!')
    def erase_data(self):
        self.lstb_var.set('')
        self.l_count_var.set('')
    
    def start_widget(self):
        self.build_widgets()
        self.btn_clean_all['state'] = 'normal'
        self.lstb.bind('<Double-2>', lambda x: self.insert_data())
        self.lstb.bind('<Double-3>', lambda x: self.erase_data())
        self.grid_inner_widgets()


class ConclsManualInputTestWithCanvas(ttk.Frame, CommonInterface):
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        CommonInterface.__init__(self, parent)
        self.canvas = None
        self.inner_frame = None
        self.scrl_y = None
        self.label_article = None
        self.label_theme = None
        self.label_concl = None
        self.label_pos = None
        self.label_anno = None
        self.txt_article = None
        self.txt_theme = None
        self.txt_concl = None
        self.txt_pos = None
        self.txt_anno = None

    def build_widgets(self):
        self.canvas = tk.Canvas(
            self,
            width=400,
            height=400,
            scrollregion=(0, 0, 400, 2000),
            highlightthickness=0
        )
        self.scrl_y = ttk.Scrollbar(
            self,
            orient='vertical',
            command=self.canvas.yview
        )
        self.canvas['yscrollcommand'] = self.scrl_y.set
        
        self.inner_frame = ttk.Frame(self.canvas)
        
        self.label_article = ttk.Label(
            self.inner_frame,
            text='Введите номер и заголовок статьи:'
        )
        self.label_theme = ttk.Label(
            self.inner_frame,
            text='Введите название раздела, в который помещен вывод:'
        )
        self.label_concl = ttk.Label(
            self.inner_frame,
            text='Введите вывод:'
        )
        self.label_pos = ttk.Label(
            self.inner_frame,
            text='Введите позицию (если есть):'
        )
        self.label_pos = ttk.Label(
            self.inner_frame,
            text='Введите аннотацию вывода или позиции (если есть):'
        )

        self.txt_article = tkst.ScrolledText(
            self.inner_frame,
            width=45,
            height=5,
        )
        self.txt_theme = tkst.ScrolledText(
            self.inner_frame,
            width=45,
            height=5,
        )
        self.txt_concl = tkst.ScrolledText(
            self.inner_frame,
            width=45,
            height=5,
        )
        self.txt_pos = tkst.ScrolledText(
            self.inner_frame,
            width=45,
            height=5,
        )
        self.txt_anno = tkst.ScrolledText(
            self.inner_frame,
            width=45,
            height=5,
        )

    def grid_inner_widgets(self):
        self.canvas.grid(column=0, row=0, sticky='nwse')
        self.scrl_y.grid(column=1, row=0, sticky='nws')
        #self.inner_frame.grid(column=0, row=0, sticky='nwse')
        self.canvas.create_window(
            (0,0),
            window=self.inner_frame,
            anchor='nw'
        )
        widgets = (
            self.label_article,
            self.txt_article,
            self.label_theme,
            self.txt_theme,
            self.label_concl,
            self.txt_concl,
            self.label_pos,
            self.txt_pos,
        )
        for ind, widget in enumerate(widgets):
            widget.grid(column=0, row=ind, sticky='nw')


if __name__ == '__main__':
    mode = sys.argv[1]
    root = tk.Tk()
    if mode == '-l':
        lvt = ListViewTest(root)
        lvt.start_widget_solo()
    if mode == '-m':
        cmi = ConclsManualInput(root)
        cmi.start_widget_solo()