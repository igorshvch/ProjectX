from time import time

def timer(func):
    def wrapper(*args, **kwargs):
        local_timer = time()
        print('-'*69)
        res = func(*args, **kwargs)
        end_time = time() - local_timer
        print(
            'TIME: {:.3f} min ({:.3f} sec)'.format(
                end_time/60, end_time
            )
        )
        print('-'*69)
        return res
    return wrapper

def timer_with_func_name(func):
    def wrapper(*args, **kwargs):
        local_timer = time()
        print('-'*69)
        print('===========>DO: {:.>53}'.format(func.__name__))
        res = func(*args, **kwargs)
        print('======>COMLETE: {:.>53}'.format(func.__name__))
        end_time = time() - local_timer
        print(
            '=========>TIME: {:.3f} min ({:.3f} sec)'.format(
                end_time/60, end_time
            )
        )
        print('-'*69)
        return res
    return wrapper

def timer_message(stmt):
    def decorator(func):
        def wrapper(*args, **kwargs):
            local_timer = time()
            print('-'*69)
            print('===========>DO: {}'.format(stmt))
            res = func(*args, **kwargs)
            print('======>COMLETE: {}'.format(stmt))
            end_time = time() - local_timer
            print(
                '=========>TIME: {:.3f} min ({:.3f} sec)'.format(
                    end_time/60, end_time
                )
            )
            print('-'*69)
            return res
        return wrapper
    return decorator