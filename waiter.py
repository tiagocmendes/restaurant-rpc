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
                        logging.FileHandler("{0}/{1}.log".format('./log_files', 'waiter'), mode='w'),
                        logging.StreamHandler()
                    ])


def main(ip, port):
    # create a logger for the waiter
    logger = logging.getLogger('Waiter')
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    current_order = {}

    while True:
        while True:
            logger.info('Get items request')
            p = pickle.dumps({"method": GET_ITEMS})
            socket.send(p)
        
            p = socket.recv()
            o = pickle.loads(p)
            logger.info('Received %s', o)

            if o != None:
                break

            # waiting for items
            work(5)
        

        item = o[0]
        order_id = o[1][0]
        quantity = o[1][1]

        logger.info('Get original order')
        p = pickle.dumps({"method": GET_ORIGINAL_ORDER, "args": order_id})
        socket.send(p)

        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Received %s', o)

        logger.info('Adding {0} {1} in order No.{2}'.format(str(quantity),str(item),str(order_id)))
        for i in range(quantity):
            if order_id in current_order:
                current_order[order_id].append(item)
            else:
                current_order[order_id] = [item]
            
        if len(current_order[order_id]) == len(o):
            while True:
                logger.info('Request client payment of order No. ' + str(order_id))
                p = pickle.dumps({"method": REQ_PAYMENT, "args": order_id})
                socket.send(p)

                p = socket.recv()
                o = pickle.loads(p)
                logger.info('Got %s', o)

                if o == True:
                    break
                    
                work(5)
            
            logger.info('Delivering order No. ' + str(order_id))
            p = pickle.dumps({"method": DELIVERING, "args": (order_id, current_order[order_id])})
            socket.send(p)

            p = socket.recv()
            o = pickle.loads(p)
            logger.info('Got %s', o)

        if not o:
            break
    
    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")
