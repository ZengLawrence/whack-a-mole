'''
Created on Dec 2, 2017

@author: lawrencezeng
'''
import RPi.GPIO as GPIO
import time
from queue import Queue
from threading import Thread
from whack_a_mole import run_whack_a_mole, GAME_RUNNING
import sys

SDI   = 11
RCLK  = 12
SRCLK = 13

BUTTON_LIGHTS = [0x00, 0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x100] 
LIGHTS_OFF = 0x00

BUTTONS = [29, 31, 33, 35, 37, 32, 36, 38, 40]

# This sets whether game running
game_running = False

# input queue
input_q = Queue()
# output queue
output_q = Queue()

def button_pressed(numb):
    print("Button {} pressed".format(numb))
    input_q.put(numb)

def setup():
        GPIO.setmode(GPIO.BOARD)    # Number GPIOs by its physical location
        GPIO.setup(SDI, GPIO.OUT)
        GPIO.setup(RCLK, GPIO.OUT)
        GPIO.setup(SRCLK, GPIO.OUT)
        GPIO.output(SDI, GPIO.LOW)
        GPIO.output(RCLK, GPIO.LOW)
        GPIO.output(SRCLK, GPIO.LOW)
        # button inputs
        GPIO.setup(BUTTONS[0], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[0], GPIO.FALLING, callback=lambda x:button_pressed(1), bouncetime=200)
        GPIO.setup(BUTTONS[1], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[1], GPIO.FALLING, callback=lambda x:button_pressed(2), bouncetime=200)
        GPIO.setup(BUTTONS[2], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[2], GPIO.FALLING, callback=lambda x:button_pressed(3), bouncetime=200)
        GPIO.setup(BUTTONS[3], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[3], GPIO.FALLING, callback=lambda x:button_pressed(4), bouncetime=200)
        GPIO.setup(BUTTONS[4], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[4], GPIO.FALLING, callback=lambda x:button_pressed(5), bouncetime=200)
        GPIO.setup(BUTTONS[5], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[5], GPIO.FALLING, callback=lambda x:button_pressed(6), bouncetime=200)
        GPIO.setup(BUTTONS[6], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[6], GPIO.FALLING, callback=lambda x:button_pressed(7), bouncetime=200)
        GPIO.setup(BUTTONS[7], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[7], GPIO.FALLING, callback=lambda x:button_pressed(8), bouncetime=200)
        GPIO.setup(BUTTONS[8], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTONS[8], GPIO.FALLING, callback=lambda x:button_pressed(9), bouncetime=200)
        
def hc595_in(dat):
        for bit in range(0, 9): 
                GPIO.output(SDI, 0x100 & (dat << bit))
                GPIO.output(SRCLK, GPIO.HIGH)
                time.sleep(0.001)
                GPIO.output(SRCLK, GPIO.LOW)

def hc595_out():
        GPIO.output(RCLK, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(RCLK, GPIO.LOW)

def destroy():   # When program ending, the function is executed. 
        GPIO.cleanup()

def light_output():
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
            hc595_in(BUTTON_LIGHTS[cell])
            hc595_out()
            print("{} on...".format(cell))
        else:
            hc595_in(LIGHTS_OFF)
            hc595_out()
            print("...{} off".format(cell))

def start_light_output_thread():
    output_t = Thread(target=light_output)
    output_t.daemon = True
    output_t.start()

def test(output_q, input_q):
    button = 0
    while button < 10:
        input = None
        try:
            input = input_q.get(block=False)
        except Empty:
            # don't care if queue is empty, get it next time
            input = None
        if input == button:
            button = button + 1
            output_q.put(button)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test(output_q, input_q)
    run_whack_a_mole(output_q, input_q)

if __name__ == '__main__':
    setup()
    start_light_output_thread()
    try:
        main()
    finally:
        destroy()
