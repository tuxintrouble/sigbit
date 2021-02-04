#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# Hardware Abstraction Classes for sidetone generation on PC and ESP

from util import ditlen, encode
import numpy as np


class SDSidetone():
    """cPython Sounddevice based Sidetone functions with true Sinewave"""

    def __init__(self):

        import time
        import sounddevice as sd


        self.freq = 0 #default values will change
        self.wpm = 0 #default values will change

        #self.fs = sd.query_devices("default")["default_samplerate"]
        self.fs = sd.query_devices(sd.default.device[1])["default_samplerate"]
        sd.default.blocksize = 2048
        sd.default.channels = 1
        sd.default.latency=0.1

        self.Stim = sd.OutputStream(dtype='int16')
        self.Stim.start()

        self.dit_sine = None
        self.dah_sine = None
        self.recompute_tones(18, 550)

    def recompute_tones(self,wpm,freq):
        #only calculate sinewaves when freq and ditlen have changed to save some cpu time
        if self.freq == freq and self.wpm == wpm:
            return
        else:
            #only calculate sinewaves when freq and ditlen have changed to save some cpu time
            #make a sinewave one dit long
            t = ditlen(wpm)
            samples = np.arange(t * self.fs) / self.fs
            signal = np.sin(2 * np.pi * freq * samples)
            signal *= 32767
            signal = np.int16(signal)
            self.dit_sine = signal
            #fade in
            fade_in_end = 200
            fade_in_sample = 0
            percent_per_sample = 1 / fade_in_end
            while fade_in_sample < fade_in_end:
                self.dit_sine[fade_in_sample] = int(self.dit_sine[fade_in_sample] * percent_per_sample * fade_in_sample)
                fade_in_sample +=1
            #fade out
            fadesample = -300
            percent_per_sample = 1 / fadesample
            while fadesample < 0:
                self.dit_sine[fadesample] = int(self.dit_sine[fadesample] * percent_per_sample * fadesample)
                fadesample +=1
            
            #make a sinewave one dah long
            t = 3*ditlen(wpm)
            samples = np.arange(t * self.fs) / self.fs
            signal = np.sin(2 * np.pi * freq * samples)
            signal *= 32767
            signal = np.int16(signal)
            self.dah_sine = signal
            #fade in
            fade_in_end = 200
            fade_in_sample = 0
            percent_per_sample = 1 / fade_in_end
            while fade_in_sample < fade_in_end:
                self.dah_sine[fade_in_sample] = int(self.dah_sine[fade_in_sample] * percent_per_sample * fade_in_sample)
                fade_in_sample +=1
            #fade out
            fadesample = -300
            percent_per_sample = 1 / fadesample
            while fadesample < 0:
                self.dah_sine[fadesample] = int(self.dah_sine[fadesample] * percent_per_sample * fadesample)
                fadesample +=1



            #set new values for frq and wpm
            self.wpm = wpm
            self.freq = freq

    def play_dit(self):
        """plays a dit tone in the soundcard, non blocking, returns start time of sound"""
        import threading, time
        t = threading.Thread(target=self.Stim.write, args = [self.dit_sine])
        t.start()
        return time.time() #return the time when sound has started

    def play_dah(self):
        import threading, time
        """plays a dah tone in the soundcard, non blocking, returns start time of sound"""
        t = threading.Thread(target=self.Stim.write, args = [self.dah_sine])
        t.start()
        return time.time() #return the time when sound has started

    def play_text(self, text):
        """Play a text as morse code"""
        self.play_buffer(encode(text))


    def play_buffer(self, buffer):
        """Play a buffer as morse code"""
        import time
        for el in buffer:
            if el == "01":
                self.play_dit()
                time.sleep(2 * ditlen(self.wpm))
            elif el == "10":
                self.play_dah()
                time.sleep(4 * ditlen(self.wpm))
            elif el == "00":
                time.sleep(3 * ditlen(self.wpm))




class PWMSideTone():
    """uPython PWM based Sidetone functions with square wave"""

    def __init__(self, pwmpin):

        import machine, utime
        self.pwm = machine.PWM(machine.Pin(pwmpin))
        self.pwm.duty(0)
        self.pwm.deinit()
        self.pwm.freq(tone)
	
        self.eot_timer = machine.Timer(1) #timer for ending tones

        self.freq = 650 #default values will change
        self.wpm = 18 #default values will change

        self.dit_sine = None
        self.dah_sine = None

        self.recompute_tones(self.wpm, self.freq)

    def recompute_tones(self,wpm,freq):
        """call whenever we change wpm or tone freq.
        this is not really necessary for pwm tones, but we keep it for HAL consistency"""
        if not (self.freq == freq and self.wpm == wpm):
            #set new values for frq and wpm
            self.wpm = wpm
            self.freq = freq

    def end_of_tone(self):
        """callback function for ending pwm tones"""
        self.pwm.duty(0)
        self.pwm.deinit()

    def play_dit(self):
        """plays a dit tone on PWM pin, non blocking, returns start time of sound"""
        tl = ditlen(self.wpm)
        self.pwm.duty(self.freq)
        self.eot_timer.init(mode = machine.Timer.ONE_SHOT, period = tl, callback = self.end_of_tone)
        return utime.ticks_ms() / 1000 #tone starting time in seconds

    def play_dah(self):
        """plays a dit tone on PWM pin, non blocking, returns start time of sound"""
        tl = ditlen(self.wpm) * 3
        self.pwm.duty(self.freq)
        self.eot_timer.init(mode = machine.Timer.ONE_SHOT, period = tl, callback = self.end_of_tone)
        return utime.ticks_ms() / 1000 #tone starting time in seconds

    def play_text(self, text):
        """Play a text as morse code"""
        self.play_buffer(encode(text))


    def play_buffer(self, buffer):
        """Play a buffer as morse code"""
        import time
        for el in buffer:
            if el == "01":
                self.play_dit()
                time.sleep(2 * ditlen(self.wpm))
            elif el == "10":
                self.play_dah()
                time.sleep(4 * ditlen(self.wpm))
            elif el == "00":
                time.sleep(3 * ditlen(self.wpm))

