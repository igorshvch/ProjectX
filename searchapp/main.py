from searchapp.gui.dialogs import ffp, fdp
import searchapp.textproc as textproc
from time import strftime

class InfoBank():
    def __init__(self):
        pass

class PrintCenter():
    def __init__(self):
        pass
    
    def print_current_time(self):
        return strftime(r'%Y/%m/%d_%H:%M:%S')

INFOBANK = InfoBank()
PRINTCENTER = PrintCenter()

def add_data_files():
    path_to_dir = fdp()
    filepaths = textproc.collect_exist_files(path_to_dir, suffix='.txt')
    res_text = ''
    for path in filepaths:
        res_text += textproc.read_text(path, encoding='utf-8')
    GLOBALHOLDER.text_of_all_concls = res_text
    ###

