
import sys
from multiprocessing import Process, freeze_support, Queue
sys.path.append('..')
import logging
logging.basicConfig()
from speech import *

if __name__ == '__main__':
    freeze_support()
    q = Queue()
    q2 = Queue()
    p = Process(target=speech_main,args=(q,q2))    
    p.start()

    from gui import *
    p2 = Process(target=run,args=(MainWidget,q,q2))
    p2.start()
 