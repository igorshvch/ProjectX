import os
import pathlib

if __name__ == '__main__':
    print(os.getcwd())
    print(os.path.dirname(__file__))
    print(pathlib.Path(__file__).parent)