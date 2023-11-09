#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# main executable for SigBit client

import threading, time, sys
from datetime import datetime
from key import SerialKey as Key
from sidetone import SDSidetone as Sidetone
from keyer import Keyer
from util import morse, decode, encode
from trx import *
from appconfig import AppConfig


__version__= "0.1"

DEBUG=1
LOG=0

def debug(s):
    if DEBUG:
        print(datetime.now().strftime("%d-%m-%Y, %H:%M:%S -") + s)
        if LOG:
          logfile = open("SigBitLog.txt","a")
          logfile.write((datetime.now().strftime("%d-%m-%Y, %H:%M:%S -") + s+"\n"))
          logfile.close()

cfg = AppConfig("SigBitTRX","DJ5SE",__version__)

server_url = cfg.get('server_url')
server_port = cfg.getint("server_port")
serial_port = cfg.get("serial_port")
sidetone_freq = cfg.getint("sidetone_freq")
keyer_speed = cfg.getint("keyer_speed")
AUTORECONNECT = cfg.getboolean('autoreconnect')
decode_cw = cfg.getboolean("decode_cw")

last_msg_recv = 0
connected_to_server = True

key = Key(serial_port)
buzzer = Sidetone()
buzzer.recompute_tones(keyer_speed,sidetone_freq)
keyer = Keyer(key, buzzer)
trx = TRX( buzzer,url=(server_url,server_port),timeout=0)

if __name__ == "__main__":

    print("SigBit %s by DJ5SE" % __version__)
    print("-"*60)
    print("Using server '%s' on port %i."%(server_url,server_port))
    print("Serial port: '%s'" % serial_port)
    print("Your user config file is here:\n'%s'" % cfg.config_file_name)
    print("-"*60)
    print("Keyer speed: %sWPM" % keyer_speed)
    print("Tone frequency: %sHz" % sidetone_freq)
    print("-"*60)
    print("Send morse code 'hi' to connect to server.")
    print("Send morse code ':qrt' to disconnect before exiting client.")
    print("Use Ctrl + C to exit.")
    print("-"*60)

    print ("Try to connect")
    trx.sendto(trx.encode_buffer(encode("hi"), buzzer.wpm), (server_url,server_port))
    print ("Done")

    while KeyboardInterrupt:
        try:      
            buffer = keyer.process_iambic()
            if buffer != None:
                ##TODO filter for commands here
                trx.sendto(trx.encode_buffer(buffer, buzzer.wpm), (server_url,server_port))
                if decode_cw:
                    print(decode(buffer))

            if keyer.state == "state_start":
                time.sleep(0.05)
                data = trx.recv()

                if data == b'': #got keepalive
                    last_msg_recv = time.time()
                    debug("heartbeat received")
                    if AUTORECONNECT and connected_to_server:
                        trx.sendto(b'', (server_url,server_port)) #send heartbeat back
                        debug("heartbeat replied")
                    else:
                        pass

                elif data != None:
                    debug(str(data))
                    last_msg_recv = time.time()
                    #recalculate buzz for recv speed and tone
                    recv_speed = trx.decode_header(data)[2]
                    debug("recv_speed: %i" %recv_speed)
                    buzzer.recompute_tones(recv_speed,sidetone_freq)
                    if decode_cw:
                        print(decode(trx.decode_payload(data)))
                    buzzer.play_buffer(trx.decode_payload(data))
                    #restore buzz for send speed and tone
                    buzzer.recompute_tones(keyer_speed,sidetone_freq)

            #if received no packets from server for more than 60 secs, try to reconnect.
            #this way we can reconnect in case we got a new IP after 24hrs
            #we use a long timeout as longer transmissions might prevent the client from receiving
            if last_msg_recv + 60 < time.time() and AUTORECONNECT and connected_to_server: 
                trx.sendto(trx.encode_buffer(encode("hi"), buzzer.wpm), (server_url,server_port))
                last_msg_recv = time.time()#only reconnect once and check again in 60 secs
                debug("reconnect request sent as we lost contact to server")
                
                    
        except (KeyboardInterrupt, SystemExit):
            buzzer.play_buffer(encode("<sk> e e"))
            sys.exit()
