import sys
from pathlib import Path

def create_batch_command():
    string = 'start ""'
    ent = str(Path(sys.executable).parent.joinpath('pythonw.exe'))
    script = str(Path(__file__).parent.joinpath('simplegui.pyw'))
    string+= ' "{}" "{}"'.format(ent, script)
    return string

def create_batch_file():
    name = 'Налоговый робот.bat'
    filepath = Path(__file__).parent.joinpath(name)
    with open(filepath, mode='w') as f:
        f.write(create_batch_command())

if __name__ == '__main__':
        create_batch_file()