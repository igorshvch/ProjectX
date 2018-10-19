import multiprocessing as mpc
from queue import Empty as queueErrorEmpty

def data_supplier(queue, queue_len, func, *args):
    res = func(*args):
    for item in res:
        queue.put(item)
    pass