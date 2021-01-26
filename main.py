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
from util import morse, decode, encode
from trx import *
from appconfig import AppConfig

__version__= "0.1"

cfg = AppConfig("SigBitTRX","DJ5SE",__version__)

server_url = cfg.get('server_url')
server_port = cfg.getint("server_port")
serial_port = cfg.get("serial_port")
sidetone_freq = cfg.getint("sidetone_freq")
keyer_speed = cfg.getint("keyer_speed")
AUTORECONNECT = cfg.getboolean('autoreconnect')
decode_cw = cfg.getboolean("decode_cw")

key = Key(serial_port)
buzzer = Sidetone()
buzzer.recompute_tones(keyer_speed,sidetone_freq)
keyer = Keyer(key, buzzer)
trx = TRX( buzzer,url=(server_url,server_port),timeout=0)

if __name__ == "__main__":

    while True:
        buffer = keyer.process_iambic()
        if buffer != None:
            trx.sendto(trx.encode_buffer(buffer, buzzer.wpm), (server_url,server_port))
            print(decode(buffer))

        if keyer.state == "state_start":
            time.sleep(0.05)
            data = trx.recv()

            if data == b'': #got keepalive
                if AUTORECONNECT:
                    trx.sendto(b'', (server_url,server_port)) #send heartbeat back
                else:
                    pass

            elif data != None:
                print(decode(trx.decode_payload(data)))
                buzzer.play_buffer(trx.decode_payload(data))