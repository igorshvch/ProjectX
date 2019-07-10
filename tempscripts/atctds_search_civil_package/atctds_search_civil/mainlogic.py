from atctds_search_civil import simplegui as smg
import multiprocessing as mpc

class MainLogic(smg.MainFrame):
    def __init__(self, parent):
        smg.MainFrame.__init__(self, parent)
        self.build_widgets()
    
    def connections(self):
        self.widgets['FileManager'].retrieve('btn_CD')
    


if __name__ == '__main__':
    ml = MainLogic(smg.tk.Tk())
    ml.start_widget_solo()
        