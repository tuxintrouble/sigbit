#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# main executable for SigBit client

import threading, time
from key import SerialKey as Key
from sidetone import SDSidetone as Sidetone
from keyer import Keyer
from util import morse, decode
from trx import *

server_url = "morse.dyndnss.net"
server_port = 7373
key = Key("/dev/ttyUSB0")
buzzer = Sidetone()
buzzer.recompute_tones(20,700) #speed in wpm | tone freq in Hz
keyer = Keyer(key, buzzer)
trx = TRX( buzzer,url=(server_url,server_port),timeout=0)

if __name__ == "__main__":

    while True:
        buffer = keyer.process_iambic()
        if buffer != None:
            trx.sendto(trx.encode_buffer(buffer, buzzer.wpm), (server_url,server_port))

        if keyer.state == "state_start": 
            time.sleep(0.05)
            data = trx.recv()
            if data != None and data !=b'':
                buzzer.play_buffer(trx.decode_payload(data))
