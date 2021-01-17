#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# iambic keyer implementation 


from util import ditlen

try:
    import utime as time #uPython
except:
    import time #cPython

###implements an IAMBIC Keyer###

class Keyer():
    """Keyer Class runs the mainloop and state machine"""
    def __init__(self,key,buzzer):
        self.key = key #HAL Key object
        self.buzzer = buzzer# HAL sidetone object

        ###States###
        self.state = "state_start" #state_dit state_dah state_echar state_eword
        self.dit_latch = False
        self.dah_latch = False

        self.sound_started = time.time() #when was the sound started last time?
        self.char_pause_started = time.time()
        self.word_pause_started = time.time()

        ###Buffers###
        self.el_buffer = []
        self.char_buffer = []
        self.word_buffer = []

        
    def process_iambic(self):
        """keyer state machine, returns a word buffer or None"""

        if self.state == "state_start":
            """default state wait for something to happen"""
            if self.key.dit():
                self.state = "state_dit"

            elif self.key.dah():
                self.state = "state_dah"
                
        elif self.state == "state_dit":
                if self.key.dah():
                        self.dah_latch = True
                        
                #put element in buffer here
                self.el_buffer.append("01")
                self.sound_started = self.buzzer.play_dit()

                while self.sound_started + (2 *ditlen(self.buzzer.wpm)) > time.time():
                        
                        if self.key.dah():
                                self.dah_latch = True
                if self.key.dit():
                        self.dit_latch = True
                        
                if self.dah_latch:
                        self.state = "state_dah"
                elif self.dit_latch:
                        self.state = "state_dit"
                else:
                        self.state = "state_echar"
                        self.char_pause_started = time.time()
                self.dah_latch = self.dit_latch = False


        elif self.state == "state_dah":
                if self.key.dit():
                        self.dit_latch = True

                #put element in buffer here
                self.el_buffer.append("10")
                
                self.sound_started = self.buzzer.play_dah()
                
                while self.sound_started + (4 *ditlen(self.buzzer.wpm)) > time.time():
                        if self.key.dit():
                                self.dit_latch = True
                
                if self.key.dah():
                        self.dah_latch = True

                if self.dit_latch:
                        self.state = "state_dit"
                elif self.dah_latch:
                        self.state = "state_dah"
                else:
                        self.state = "state_echar"
                        self.char_pause_started = time.time()
                self.dah_latch = self.dit_latch = False


        elif self.state == "state_echar":
                
            
                if self.char_pause_started + (1.2 * ditlen(self.buzzer.wpm)) > time.time():

                        if len(self.el_buffer) !=0:
                                self.char_buffer.extend(self.el_buffer)
                                self.char_buffer.append("00")
                                self.el_buffer = []
                        
                        if self.key.dit():
                                self.state = "state_dit"
                        elif self.key.dah():
                                self.state = "state_dah"
                else:
                        self.state = "state_eword"
                        self.word_pause_started = time.time()   
        
        elif self.state == "state_eword":
                
                if self.word_pause_started + (3.2*ditlen(self.buzzer.wpm)) > time.time():
                        if self.key.dit():
                                self.state = "state_dit"
                        elif self.key.dah():
                                self.state = "state_dah"
                else:
                        self.state = "state_start"
                        #put char in buffer here                
                        self.word_buffer = self.char_buffer
                        self.word_buffer.pop()
                        self.word_buffer.append("11")
                        self.char_buffer = []
                        buffer = self.word_buffer
                        word_buffer = []
                        return buffer
