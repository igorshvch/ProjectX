import sys
import pathlib as pthl

dir_structure = [
    (
        'Оглавление ПСП',
        'Стоп-слова'
    
    ),
    (
        '_Работа программы',
        '01 Судебные акты',
        '02 Выводы с аннотациями',
        '03 Результаты',
        '04 Предыдущие сеансы'
    ),
    ('Робот',),
]

def create_dir_struct(root, dir_struct):
    dirs = dir_struct.pop()
    for i in dirs:
        root = root + '/' + i
        print(root)
        create_dir_struct(root, dir_struct)

def create_save_folder(root, folder_name):
    path_obj = pthl.Path(root).joinpath(folder_name)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj

###############################################################################

def create_batch_command(mode='win'):
    if mode == 'win':
        string = 'start "" "{}" "{}"'
        entrp_v = 'pythonw.exe'
        script_v = 'simplegui.pyw'
    elif mode == 'cmd':
        string = 'start {} {}'
        entrp_v = 'python.exe'
        script_v = 'simplegui.py'
    entrp = str(pthl.Path(sys.executable).parent.joinpath(entrp_v))
    script = str(pthl.Path(__file__).parent.joinpath(script_v))
    return string.format(entrp, script)

def create_batch_file():
    name_win = 'Налоговый робот.bat'
    name_cmd = 'Налоговый робот консоль.bat'
    for name, mode in zip((name_win, name_cmd), ('win', 'cmd')):
        filepath = pthl.Path(__file__).parent.joinpath(name)
        with open(filepath, mode='w') as f:
                f.write(create_batch_command(mode=mode))