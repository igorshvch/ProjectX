import multiprocessing as mpc
from multiprocessing import Queue
from queue import (
    Empty as queueErrorEmpty,
    Full as queueErrorFull
)
from time import sleep
import random
import tkinter as tk
from tkinter import ttk

def producer(lock, queue, iterator):
    '''
    Accept itterator to fullfil the queue
    '''
    with lock:
        print(
            'Producer', mpc.current_process().name
        )
    for item in iterator:
        queue.put(item)


def consumer(lock, ind, queue):
    while True:
        sleep(random.randint(1,2))
        if queue.empty():
            with lock:
                print(
                    'IND: {}'.format(ind), mpc.current_process().name,
                    'Process end, bye!'
                )
            break
        item = queue.get()
        with lock:
            print(
                'IND: {}'.format(ind), mpc.current_process().name,
                'get item!', 'Item # {}'.format(item)
            )

def launcher():
    lock = mpc.Lock()
    queue = Queue(maxsize=3)
    gen = [i for i in range(24)]
    prod = mpc.Process(target=producer, args=(lock, queue, gen))
    prod.start()
    cons = [
        mpc.Process(target=consumer, args=(lock, i, queue))
        for i in range(3)
    ]
    for i in cons:
        i.start()
    prod.join()
    for i in cons:
        i.join()

if __name__ == '__main__':
    print('START!')
    launcher()