'''
Whack-a-mole with simulator for GPIO queues.
'''
import whack_a_mole
from queue import Queue
from threading import Thread
from whack_a_mole import run_whack_a_mole, GAME_RUNNING
import random
from time import sleep

# This sets whether game running
game_running = False

# output queue
output_q = Queue()

def console_output():
    global game_running
    while True:
        cell, is_on = output_q.get()
        if cell == GAME_RUNNING:
            game_running = is_on
            if game_running:
                print("Game starts")
            else:
                print("Game over")
            continue
        
        if is_on:
            print("{} on...".format(cell))
        else:
            print("...{} off".format(cell))

output_t = Thread(target=console_output)
output_t.daemon = True
output_t.start()

# input queue
input_q = Queue()

def random_input():
    global game_running
    games_to_play = 3
    while True:
        sleep(0.5)
        if game_running:
            guess = random.randint(1, 9)
            print("guess {}".format(guess))
            input_q.put(guess)
        else:
            if games_to_play > 0:
                print("Yes to start game")
                input_q.put("Y")
                games_to_play = games_to_play -1
            else:
                print("No to quit the game")
                input_q.put("N")
            

input_t = Thread(target=random_input)
input_t.daemon = True
input_t.start()

# run Whack a Mole
run_whack_a_mole(output_q, input_q)
