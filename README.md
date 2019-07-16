# restaurant-rpc
### Distributed Systems | UA 2018/2019

**Description:** This repository implements a drive-through restaurant using a centralized distributed system architecture based on remote procedure calls. 

* Create a virtual environment and install requirements:
```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

* How to run:
```console
$ ./run.sh [number_of_client.py_processes]
```
* Example:
```console
$ ./run.sh 3
Starting drive-through.py background process
Starting clerk.py background process
Starting chef.py background process
Starting waiter.py background process
Starting client.py No. 1 background process
Starting client.py No. 2 background process
Starting client.py No. 3 background process
```

* To kill the processes and remove log files:
```console
$ ./clean.sh
```

<br/>**Useful links:**
  * Work objectives: [CD2019G02.pdf](https://github.com/detiuaveiro/restaurante-drive-through-tiagocmendes/blob/master/CD2019G02.pdf)
  * Python random: [https://docs.python.org/3/library/random.html#module-random](https://docs.python.org/3/library/random.html#module-random)
  * Python time: [https://docs.python.org/3/library/time.html#time.sleep](https://docs.python.org/3/library/time.html#time.sleep)
  * Python logging: [https://docs.python.org/3/library/logging.html?highlight=log#module-logging](https://docs.python.org/3/library/logging.html?highlight=log#module-logging)
  * Python pickle: [https://docs.python.org/3/library/pickle.html](https://docs.python.org/3/library/pickle.html)
  * Python signal: [https://docs.python.org/3.7/library/signal.html](https://docs.python.org/3.7/library/signal.html)
  * Python oop: [https://python.swaroopch.com/oop.html](https://python.swaroopch.com/oop.html)
  * Python classes: [https://docs.python.org/3/tutorial/classes.html](https://docs.python.org/3/tutorial/classes.html)
  * zeroMQ: [http://zeromq.org/](http://zeromq.org/)
  * Shared Queue (DEALER and ROUTER sockets): [http://zguide.zeromq.org/py:all#Shared-Queue-DEALER-and-ROUTER-sockets](http://zguide.zeromq.org/py:all#Shared-Queue-DEALER-and-ROUTER-sockets)
  * Multithreading with ZeroMQ [http://zguide.zeromq.org/py:all#Multithreading-with-ZeroMQ](http://zguide.zeromq.org/py:all#Multithreading-with-ZeroMQ)

**Author:** Tiago Mendes
