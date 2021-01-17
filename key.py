#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# Hardware Abstraction Classes for interfacing with iambic keys

from util import ditlen

###Hardware Abstraction Classes###
# must implement the functions dit() and dah()
# which return True if Paddle is pressed

class GPIOKey():
    """GPIO based key implementation for ESP32 and micropython, takes pin numbers as arguments"""


    def __init__(self,ditpin, dahpin):
        import machine
        import utime as time

        self.debounce_factor = 0.001 #sec

        self.last_time_dit = time.time()
        self.last_time_dah = time.time()

        self.ditpin = machine.Pin(ditpin, mode = machine.Pin.IN, pull = machine.Pin.PULL_UP)
        self.dahpin = machine.Pin(dahpin, mode = machine.Pin.IN, pull = machine.Pin.PULL_UP)

    def dit(self):
        if self.last_time_dit + self.debounce_factor < time.time() and self.ditpin.value():
            self.last_time_dit = time.time()
            return True
        else:
            return False

    def dah(self):
        if self.last_time_dah + self.debounce_factor < time.time() and self.dahpin.value():
            self.last_time_dah = time.time()
            return True
        else:
            return False

class SerialKey():
    """Serial based key implementation for cPython, takes a port as argument (COM1,/dev/ttyUSB0") """


    
    def __init__(self, port):
        import serial,time
        
        self.debounce_factor = 0.001 # sec
    
        self.ser = serial.Serial(port)
        self.last_time_dit = time.time()
        self.last_time_dah = time.time()
        
    def dit(self):
        import time
        if self.last_time_dit + self.debounce_factor < time.time() and self.ser.getDSR():
            self.last_time_dit = time.time()
            return True
        else:
            return False

    def dah(self):
        import time
        if self.last_time_dah + self.debounce_factor < time.time() and self.ser.getCTS():
                self.last_time_dah = time.time()
                return True
        else:
                return False
