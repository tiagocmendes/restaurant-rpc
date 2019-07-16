# coding: utf-8
import uuid
import logging
import threading
import pickle
from queue import Queue
from request import * 
import zmq
from utils import *

# configure the log with DEBUG level
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[
                        logging.FileHandler("{0}/{1}.log".format('./log_files', 'drive-through'), mode='w'),
                        logging.StreamHandler()
                    ])



class Worker(threading.Thread):
    def __init__(self, context, i, backend, restaurant):
        # call the constructor form the parent class
        threading.Thread.__init__(self)

        self.socket = context.socket(zmq.REP)
        self.backend = backend
        self.restaurant = restaurant

        # store the necessary inputs
        self.logger = logging.getLogger('Worker '+str(i))

    def run(self):
        self.socket.connect(self.backend)

        self.logger.info('Start working')
        while True:
            p = self.socket.recv()
            o = pickle.loads(p)
            self.logger.info('\n')
            
            # client RPC
            if o["method"] == FOOD_REQUEST:
                self.logger.info('CLIENT RPC:')
                self.logger.info('Received FOOD_REQUEST method with args ' + str(o["args"]))
                order_id = self.restaurant.add_order(o["args"])
                self.logger.info('Sending FOOD_REQUEST response: ' + str(order_id))
                p = pickle.dumps(order_id)
            
            # clerk RPC
            elif o["method"] == REQ_TASK:
                self.logger.info('CLERK RPC:')
                self.logger.info('Received REQ_TASK method')
                task = self.restaurant.get_task()
                self.logger.info('Sending REQ_TASK response: ' + str(task))
                p = pickle.dumps(task)
            
            # clerk RPC
            elif o["method"] == TASK_READY:
                self.logger.info('CLERK RPC:')
                self.logger.info('Received TASK_READY method with args ' + str(o["args"]))
                self.restaurant.split_order(o["args"])
                self.logger.info('Sending TASK_READY response: ' + str(True))
                p = pickle.dumps(True)
            
            # chef RPC
            elif o["method"] == ITEM_REQUEST:
                self.logger.info('CHEF RPC:')
                self.logger.info('Received ITEM_REQUEST method')
                item = self.restaurant.item_request()
                self.logger.info('Sending ITEM_REQUEST response: ' + str(item))
                p = pickle.dumps(item)
            
            # chef RPC
            elif o["method"] == MAKE_ITEM:
                self.logger.info('CHEF RPC:')
                self.logger.info('Received MAKE_ITEM method with args: ' + str(o["args"]))
                
                if o["args"] == 'DRINK':
                    self.restaurant.bar.prepare_drink()
                elif o["args"] == 'FRIES':
                    self.restaurant.fryer.to_fry()
                elif o["args"] == 'HAMBURGUER':
                    self.restaurant.barbecue_grill.to_grill()

                self.logger.info('Sending MAKE_ITEM response: ' + str(o["args"]) + ' prepared')
                p = pickle.dumps(True)
            
            # chef RPC
            elif o["method"] == FINISHED_ITEMS:
                self.logger.info('CHEF RPC:')
                self.logger.info('Received FINISHED_ITEMS method with args: ' + str(o["args"]))
                self.restaurant.ready_items(o["args"])
                self.logger.info('Sending FINISHED_ITEMS response: ' + str(True))
                p = pickle.dumps(True)
            
            # waiter RPC
            elif o["method"] == GET_ITEMS:
                self.logger.info('WAITER RPC:')
                self.logger.info('Received GET_ITEMS method')
                items =  self.restaurant.get_items()
                self.logger.info('Sending GET_ITEMS response: ' + str(items))
                p = pickle.dumps(items)
            
            # waiter RPC
            elif o["method"] == GET_ORIGINAL_ORDER:
                self.logger.info('WAITER RPC:')
                self.logger.info('Received GET_ORIGINAL_ORDER method with args: ' + str(o["args"]))
                order_items = self.restaurant.original_orders[o["args"]]
                self.logger.info('Sending GET_ORIGINAL_ORDER response: ' + str(order_items))
                p = pickle.dumps(order_items)
            
            # waiter RPC
            elif o["method"] == REQ_PAYMENT:
                self.logger.info('WAITER RPC:')
                self.logger.info('Received REQ_PAYMENT method with args: ' + str(o["args"]))
                if o["args"] in self.restaurant.payments:
                    payment = self.restaurant.payments[o["args"]]
                else:
                    payment = self.restaurant.payments[o["args"]] = False
                self.logger.info('Sending REQ_PAYMENT response: ' + str(payment))
                p = pickle.dumps(payment)
            
            # waiter RPC
            elif o["method"] == DELIVERING:
                self.logger.info('WAITER RPC:')
                self.logger.info('Received DELIVERING method with args: ' + str(o["args"]))
                self.restaurant.delivering(o["args"])
                self.logger.info('Sending DELIVERING response: ' + str(True))
                p = pickle.dumps(True)
                
            # client RPC
            elif o["method"] == PAYMENT:
                self.logger.info('CLIENT RPC:')
                self.logger.info('Received PAYMENT method with args ' + str(o["args"]))
                payment_complete = self.restaurant.payment(o["args"])
                self.logger.info('Sending PAYMENT response: ' + str(payment_complete))
                p = pickle.dumps(payment_complete)

            elif o["method"] == PICKUP:
                self.logger.info('CLIENT RPC:')
                self.logger.info('Received PICKUP method with args ' + str(o["args"]))
                order = self.restaurant.pickup(o["args"])
                self.logger.info('Sending PICKUP response: ' + str(order))
                p = pickle.dumps(order)

            self.socket.send(p)
        self.socket.close()


class DriveThrough:
    def __init__(self, logger):
        # clerk queues
        self.original_orders = {}
        self.orders = Queue()
        self.task = Queue()
        # chef queues
        self.drinks = Queue()
        self.fries = Queue()
        self.hamburgers = Queue()
        # waiter queues
        self.drinks_ready = Queue()
        self.fries_ready = Queue()
        self.hamburgers_ready = Queue()
        self.payments = {}

        self.logger = logger

        # open the config.txt file that has the preparing times of each kitchen equipment
        preparing_times = open_config_file('config.txt')

        # create 3 objects representing each kitchen equipment
        self.barbecue_grill = BarbecueGrill(preparing_times["grill"][0],preparing_times["grill"][1])
        self.logger.info('Cleaning Barbecue Grill')

        self.bar = Bar(preparing_times["bar"][0],preparing_times["bar"][1])
        self.logger.info('Opening Bar')

        self.logger.info('Changing Fryer\'s oil')
        self.fryer = Fryer(preparing_times["fry"][0],preparing_times["fry"][1])

    def add_order(self, order):
        order_id = uuid.uuid4()
        self.orders.put((order_id, order))
        self.original_orders[order_id] = order
        return order_id

    def split_order(self, order):
        order_id = order[0]
        if order[1]['DRINK'] > 0:
            self.drinks.put((order_id, order[1]['DRINK']))
        if order[1]['FRIES'] > 0:
            self.fries.put((order_id, order[1]['FRIES']))
        if order[1]['HAMBURGUER'] > 0:
            self.hamburgers.put((order_id, order[1]['HAMBURGUER']))
    
    def item_request(self):
        if self.drinks.qsize() != 0:
            return ('DRINK',self.drinks.get())
        elif self.fries.qsize() != 0:
            return ('FRIES',self.fries.get())
        elif self.hamburgers.qsize() != 0:
            return ('HAMBURGUER', self.hamburgers.get())
    
    def ready_items(self, items):
        item = items[0]
        order_id = items[1][0]
        quantity = items[1][1]
        if item == 'DRINK':
            self.drinks_ready.put((order_id,quantity))
        elif item == 'FRIES':
            self.fries_ready.put(((order_id,quantity)))
        elif item == 'HAMBURGUER':
            self.hamburgers_ready.put(((order_id,quantity)))
    
    def get_items(self):
        if self.drinks_ready.qsize() != 0:
            return ('DRINK', self.drinks_ready.get())
        elif self.fries_ready.qsize() != 0:
            return ('FRIES', self.fries_ready.get())
        elif self.hamburgers_ready.qsize() != 0:
            return ('HAMBURGUER', self.hamburgers_ready.get())
    
    def delivering(self, order):
        self.task.put(order)
    
    def payment(self, order_id):
        if order_id in self.payments:
            self.payments[order_id] = True
            return True

    def pickup(self, order_id):
        if (self.task.qsize() != 0) and (str(self.task.queue[0][0]) == str(order_id)):
            return self.task.get()
    def get_task(self):
        if self.orders.qsize() != 0:
            return self.orders.get()

# Three classes representing each kitchen equipment
# Abstract class "Equipment"
class Equipment:
    def __init__(self, mean, std_deviation):
        self.mean = mean
        self.std_deviation = std_deviation
    
    def equipment_action(self):
        work_time = random.gauss(self.mean,pow(self.std_deviation,2))
        work(work_time/1000)


class BarbecueGrill(Equipment):
    def __init__(self, mean, std_deviation):
        Equipment.__init__(self, mean, std_deviation)

    
    def to_grill(self):
        Equipment.equipment_action

class Bar(Equipment):
    def __init__(self, mean, std_deviation):
        Equipment.__init__(self, mean, std_deviation)
    
    def prepare_drink(self):
        Equipment.equipment_action

class Fryer(Equipment):
    def __init__(self, mean, std_deviation):
        Equipment.__init__(self, mean, std_deviation)
    
    def to_fry(self):
        Equipment.equipment_action

def main(ip, port):
    logger = logging.getLogger('Drive-through')

    logger.info('Setup ZMQ')
    context = zmq.Context()
    restaurant = DriveThrough(logger)

    # frontend for clients (socket type Router)
    frontend = context.socket(zmq.ROUTER)
    frontend.bind("tcp://{}:{}".format(ip, port))

    # backend for workers (socket type Dealer)
    backend = context.socket(zmq.DEALER)
    backend.bind("inproc://backend")

    # Setup workers
    workers = []
    for i in range(8):
        # each worker is a different thread
        worker = Worker(context, i, "inproc://backend", restaurant)
        worker.start()
        workers.append(worker)

    # Setup proxy
    # This device (already implemented in ZMQ) connects the backend with the frontend
    zmq.proxy(frontend, backend)

    # join all the workers
    for w in workers:
        w.join()

    # close all the connections
    frontend.close()
    backend.close()
    context.term()


if __name__ == '__main__':
    main("127.0.0.1", "5001")
