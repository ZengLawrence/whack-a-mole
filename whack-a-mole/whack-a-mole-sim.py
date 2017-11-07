'''
Whack-a-mole with simulator for GPIO queues.
'''
import whack_a_mole
from queue import Queue
from threading import Thread
from whack_a_mole import run_whack_a_mole
import random
from time import sleep

# output queue
output_q = Queue()

def console_output():
    while True:
        cell, should_turn_on = output_q.get()
        if should_turn_on:
          print("{} on...".format(cell))
        else:
          print("...{} off".format(cell))

output_t = Thread(target=console_output)
output_t.daemon = True
output_t.start()

# input queue
input_q = Queue()

def random_input():
    while True:
        sleep(0.5)
        guess = random.randint(1, 9)
        print("guess {}".format(guess))
        input_q.put(guess)

input_t = Thread(target=random_input)
input_t.daemon = True
input_t.start()

# run Whack a Mole
run_whack_a_mole(output_q, input_q)
