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