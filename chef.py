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
                        logging.FileHandler("{0}/{1}.log".format('./log_files', 'chef'), mode='w'),
                        logging.StreamHandler()
                    ])


def main(ip, port):
    # create a logger for the chef
    logger = logging.getLogger('Chef')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    while True:
        while True:
            logger.info('Make item request')
            p = pickle.dumps({"method": ITEM_REQUEST})
            socket.send(p)
        
            p = socket.recv()
            o = pickle.loads(p)
            logger.info('Received %s', o)

            if o != None:
                break

            # waiting for orders
            work(5)

        item = o[0]
        order_id = o[1][0]
        quantity = o[1][1]

        logger.info('Preparing {0} {1} for order No.{2}'.format(str(quantity),str(item),str(order_id)))
        for i in range(quantity):
            p = pickle.dumps({"method":  MAKE_ITEM, "args": item})
            socket.send(p)
            p = socket.recv()
            o = pickle.loads(p)
        
        logger.info('Finished preparing {0} {1}'.format(str(quantity),str(item)))
        p = pickle.dumps({"method": FINISHED_ITEMS, "args": (item,(order_id,quantity))})
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
