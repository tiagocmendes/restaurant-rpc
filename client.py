# coding: utf-8

import logging
import math
from random import randint, gauss
import pickle
import uuid
import zmq
from utils import *
from request import *

client_id = uuid.uuid4()

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[
                        logging.FileHandler("{0}/{1}.log".format('./log_files', 'client_' + str(client_id)), mode='w'),
                        logging.StreamHandler()
                    ])


def main(ip, port):
    # create a logger for the client
    logger = logging.getLogger('Client')
    
    # setup zmq
    logger.info('Setup ZMQ')
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://{}:{}'.format(ip, port))

    # simulating client driving around the restaurant
    seconds = math.fabs(gauss(mu,sigma))
    logger.info('Client is driving around the restaurant')
    work(seconds)
    logger.info('Client arrived at the restaurant')


    logger.info('Request some food')
    
    # make a random request
    requested_items = []
    for i in range(randint(1,5)):
        item_id = randint(0,2)
        requested_items.append(possible_items[item_id])
    
    # send the request
    p = pickle.dumps({"method": FOOD_REQUEST, "args": requested_items})
    socket.send(p)
    logger.info('Client request: ' + str(requested_items))

    p = socket.recv()
    order = pickle.loads(p)
    logger.info('Order received No. %s', order)

    while True:
        logger.info('Payment intention for order No. %s', order)
        p = pickle.dumps({"method": PAYMENT, "args": order})
        socket.send(p)

        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Got %s', o)

        if o != None:
            break
        
        # wait for order completion
        work(5)

    
    logger.info('Payment complete for order No. %s' ,order)

    while True:
        logger.info('Pickup order No. %s', order)
        p = pickle.dumps({"method": PICKUP, "args": order})
        socket.send(p)

        p = socket.recv()
        o = pickle.loads(p)
        logger.info('Got %s', o)

        if o != None:
            logger.info('Order No. %s received', order)
            break
        
        work(5)
    
    logger.info('Leaving')

    socket.close()
    context.term()

    return 0


if __name__ == '__main__':
    main("127.0.0.1", "5001")
