# coding: utf-8

import logging
import pickle
import zmq
from utils import *
from request import *

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[
                        logging.FileHandler("{0}/{1}.log".format('./log_files', 'clerk'), mode='w'),
                        logging.StreamHandler()
                    ])

def main(ip, port):
    # create a logger for the client
    logger = logging.getLogger('Clerk')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    while True:
        while True:
            logger.info('Request Task')
            p = pickle.dumps({"method": REQ_TASK})
            socket.send(p)
        
            p = socket.recv()
            o = pickle.loads(p)
            logger.info('Received %s', o)

            if o != None:
                break

            # waiting for tasks
            work(5)

        # split the order by items quantity
        order = {'DRINK': 0, 'FRIES': 0, 'HAMBURGUER': 0}
        for i in range(len(o[1])):
            order[o[1][i]]+=1

        logger.info('Task Ready')
        p = pickle.dumps({"method": TASK_READY, "args": (o[0],order)})
        socket.send(p)
    
        p = socket.recv()
        o = pickle.loads(p)
        
        if not o:
            break
    

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")
