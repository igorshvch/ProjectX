import sys
from pathlib import Path

def create_batch_command(mode='win'):
    if mode == 'win':
        string = 'start "" "{}" "{}"'
        entrp_v = 'pythonw.exe'
        script_v = 'simplegui.pyw'
    elif mode == 'cmd':
        string = 'start {} {}'
        entrp_v = 'python.exe'
        script_v = 'simplegui.py'
    entrp = str(Path(sys.executable).parent.joinpath(entrp_v))
    script = str(Path(__file__).parent.joinpath(script_v))
    return string.format(entrp, script)

def create_batch_file():
    name_win = 'Налоговый робот.bat'
    name_cmd = 'Налоговый робот консоль.bat'
    for name, mode in zip((name_win, name_cmd), ('win', 'cmd')):
        filepath = Path(__file__).parent.joinpath(name)
        with open(filepath, mode='w') as f:
                f.write(create_batch_command(mode=mode))

if __name__ == '__main__':
        create_batch_file()