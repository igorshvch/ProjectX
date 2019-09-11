import re
from time import strftime

from textproc import rwtools
from tempscripts import iopickler as iop

dt_stamp = '%Y-%m-%d#%a#%H-%M-%S'

class OnDiscDictWrapper():
    def __init__(self, folder):
        self.__dict_names = (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        )
        self.folder = folder
        self.save_files = dict()
        self.files_created_flag = False
        self.create_files()
    
    def __getattr__(self, name):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        ):
            return self.__open_dict(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)
    
    def __setattr__(self, name, val):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        ):
            self.__write_dict(name, val)
        else:
            self.__dict__[name] = val
    
    def create_files(self):
        if not self.files_created_flag:
            fp = rwtools.collect_exist_files(self.folder, suffix='.dct')
            if fp:
                for file in fp:
                    name = file.name.split('#')[0]
                    self.save_files[name] = str(file)
            else:
                for dictionary in self.__dict_names:
                    name = dictionary + '#' +strftime(dt_stamp) + '.dct'
                    file = rwtools.create_new_binary(name, self.folder)
                    self.save_files[dictionary] = file.name
                    file.close()
            self.files_created_flag = True
    
    def __open_dict(self, dictionary):
        return rwtools.load_pickle(self.save_files[dictionary], mode='rb')
    
    def __write_dict(self, dictionary, val):
        rwtools.save_pickle(
            val,
            self.save_files[dictionary]
        )
    
    def erase_dict(self, dictionary):
        breaker = input(
            'You are going to delete dictionary "{}" '.format(dictionary)
            + 'entierly! Please confirm!("Y"/"N")\n'
        )
        if breaker == 'N':
            print ('Operation aborted')
            return None
        elif breaker == 'Y':
            with open(self.save_files[dictionary], mode='wb') as f:
                f.truncate(0)
        else:
            print('Incorrect command! Operation aborted')
    
    def erase_all_dicts(self):
        breaker = input(
            'You are going to delete all dictionaries'
            + 'entierly! Please confirm!("Y"/"N")\n'
        )
        if breaker == 'N':
            print ('Operation aborted')
            return None
        elif breaker == 'Y':
            for dictionary in self.save_files:
                with open(self.save_files[dictionary], mode='wb') as f:
                    f.truncate(0)
        else:
            print('Incorrect command! Operation aborted')
    
    def store_external_dicts(self, dicts_iter):
        for dictionary, dct in dicts_iter:
            print(dictionary)
            rwtools.save_pickle(
                dct,
                self.save_files[dictionary]
            )

###############################################################################
#Previouse version:############################################################
###############################################################################

class DictWithTokens():
    def __init__(self, folder):
        self.dictionaries = {
            'token_nf': dict(),
            'token_tag': dict(),
            'tag_token': dict(),
            'tag_nf': dict(),
            'nf_token': dict(),
            'nf_tag': dict()
        }
        self.folder = folder
        self.save_files = dict()
        self.files_created_flag = False
        self.files_loaded_flag = False
    
    def __getattr__(self, name):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        ):
            return self.__dict__['dictionaries'][name]
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)
    
    def __setattr__(self, name, val):
        if name in (
            'token_nf',
            'token_tag',
            'tag_token',
            'tag_nf',
            'nf_token',
            'nf_tag'
        ):
            self.__dict__['dictionaries'][name] = val
        else:
            self.__dict__[name] = val
    
    def create_files(self):
        if not self.files_created_flag and not self.files_loaded_flag:
            for dictionary in self.dictionaries:
                name = dictionary + '#' +strftime(dt_stamp)
                file = rwtools.create_new_binary(name, self.folder)
                self.save_files[dictionary] = file.name
                file.close()
            self.files_created_flag = True
    
    def load_files_from_folder(self):
        if not self.files_created_flag and not self.files_loaded_flag:
            fp = rwtools.collect_exist_files(self.folder)
            for path in fp:
                name = path.name.split('#')[0]
                self.save_files[name] = str(path)
            self.files_loaded_flag = True
    
    def open_dict(self, dictionary):
        if self.dictionaries[dictionary]:
            return self.dictionaries[dictionary]
        else:
            dct = rwtools.load_pickle(self.save_files[dictionary], mode='rb')
            if dct:
                self.dictionaries[dictionary] = dct
    
    def close_dict(self, dictionary):
        if not self.dictionaries[dictionary]:
            print('Dictionary {} is empty'. format(dictionary))
        else:
            rwtools.save_pickle(
                self.dictionaries[dictionary],
                self.save_files[dictionary]
            )
            self.dictionaries[dictionary] = dict()
    
    def erase_dict(self, dictionary):
        breaker = input(
            'You are going to delete dictionary "{}" '.format(dictionary)
            + 'entierly! Please confirm!("Y"/"N")\n')
        if breaker == 'N':
            print ('Operation aborted')
            return None
        elif breaker == 'Y':
            with open(self.save_files[dictionary], mode='wb') as f:
                f.truncate(0)
            self.dictionaries[dictionary] == dict()
        else:
            print('Incorrect command! Operation aborted')