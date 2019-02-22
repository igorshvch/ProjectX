from time import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        local_timer = time()
        print('-'*69)
        res = func(*args, **kwargs)
        end_time = time() - local_timer
        print(
            'TIME: {: >9.4f} min ({: >9.4f} sec)'.format(
                end_time/60, end_time
            )
        )
        print('-'*69)
        return res
    return wrapper

def timer_with_func_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        local_timer = time()
        print('-'*69)
        print('DO >>> {}'.format(func.__name__))
        res = func(*args, **kwargs)
        end_time = time() - local_timer
        print(
            'EVALUATION TIME: {: >9.4f} min ({: >9.4f} sec)'.format(
                end_time/60, end_time
            )
        )
        print('-'*69)
        return res
    return wrapper

def timer_message(stmt):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            local_timer = time()
            print('-'*69)
            print('===========>DO: {}'.format(stmt))
            res = func(*args, **kwargs)
            print('======>COMLETE: {}'.format(stmt))
            end_time = time() - local_timer
            print(
                '=========>TIME: {: >9.4f} min ({: >9.4f} sec)'.format(
                    end_time/60, end_time
                )
            )
            print('-'*69)
            return res
        return wrapper
    return decorator