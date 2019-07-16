import time
import argparse

mu=0.01
sigma=0.005

def work(seconds):
    time.sleep(seconds)

def open_config_file(filename):
        times = {}
        filename = open(filename,"r")
        for line in filename:
            line = line.split(";")
            times[line[0]] = (int(line[1]),int(line[2]))
        return times
