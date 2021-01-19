#!/usr/local/bin/python3
#
# This file is part of the sigbit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
# 
# Implements a chat server for the MOPP - morse over packet protocol
# on an ESP Board with micro-python
# uses code fragments from https://github.com/sp9wpn/m32_chat_server

import socket
import time
import struct
from math import ceil
from util import encode, decode, zfill, ljust

from machine import Pin

led = Pin(2, Pin.OUT)
led.on()

SERVER_IP = "0.0.0.0"
UDP_PORT = 7373
CLIENT_TIMEOUT = 60 * 10
MAX_CLIENTS = 10
KEEPALIVE = 10
DEBUG = 1
ECHO =False

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
ntp_host = "pool.ntp.org"

serversock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
serversock.bind((SERVER_IP, UDP_PORT))
serversock.settimeout(KEEPALIVE)

# (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
NTP_DELTA = 3155673600

receivers = {}

protocol_version = 1
serial = 1

def debug(str):
  if DEBUG:
    print(str)
    
def encode_buffer(buffer,wpm):

  global protocol_version
  global serial
  '''creates an bytes for sending throught a socket'''

  #create 14 bit header
  m = zfill(bin(protocol_version)[2:],2) #2bits for protocol_version
  m += zfill(bin(serial)[2:],6) #6bits for serial number
  m += zfill(bin(wpm)[2:],6) #6bits for words per minute

  #add payload
  for el in buffer:
    m += el
    
  m = ljust(m,int(8*ceil(len(m)/8.0)),'0') #fill in incomplete byte
  res = ''

  for i in range(0, len(m),8):
    res += chr(int(m[i:i+8],2)) #convert 8bit chunks to integers and the to characters

  serial +=1
  return res.encode('utf-8') #convert string of characters to bytes


def decode_header(unicodestring):
  '''converts a received morse code byte string and returns a list
  with the header info [protocol_v, serial, wpm]''' 
  bytestring = unicodestring.decode("utf-8")
  bitstring = ''
  
  for byte in bytestring:
    bitstring += zfill(bin(ord(byte))[2:],8) #works in uPython

  m_protocol = int(bitstring[:2],2)
  m_serial = int(bitstring[3:8],2)
  m_wpm = int(bitstring[9:14],2)
		
  return [m_protocol, m_serial, m_wpm]


def decode_payload(unicodestring):
  '''converts a received morse code byte string to text'''
  bytestring = unicodestring.decode("utf-8")
  bitstring = ''
	
  for byte in bytestring:
    #convert byte to 8bits
    bitstring += zfill(bin(ord(byte))[2:],8) #works in uPython

  m_payload = bitstring[14:] #we just need the payload here

  buffer =[]
  for i in range(0, len(m_payload),2):
    el = m_payload[i]+m_payload[i+1]
    buffer.append(el)

  while buffer[-1] == "00": #remove surplus '00' elements
    buffer.pop()

  return buffer


def broadcast(data,client):
  global ECHO
  global led
  led.off()
  for c in receivers.keys():
    if c == client and not ECHO:
     continue
    debug("Sending to %s" % c)
    ip,port = c.split(':')
    serversock.sendto(data, (ip, int(port)))
  led.on()

def welcome(client, speed):
  ip,port = client.split(':')
  serversock.sendto(encode_buffer(encode('welcome'),speed), addr)
  receivers[client] = time.time()
  debug("New client: %s" % client)

def reject(client, speed):
  ip,port = client.split(':')
  serversock.sendto(encode_buffer(encode(':qrl'),speed), addr)


while KeyboardInterrupt:
  time.sleep(0.2)						# anti flood
  try:
    data, addr = serversock.recvfrom(64)
    client = addr[0] + ':' + str(addr[1])
    speed = decode_header(data)[2]
    
    if client in receivers:
      if decode_payload(data) == encode(':qrt'):
        serversock.sendto(encode_buffer(encode('bye'),speed), addr)
        del receivers[client]
        debug ("Removing client %s on request" % client)
        
      elif decode_payload(data) == encode(':em'):
        if ECHO:
          ECHO = False
          serversock.sendto(encode_buffer(encode('off'),speed), addr)
        else:
          ECHO = True
          serversock.sendto(encode_buffer(encode('on'),speed), addr)

      elif decode_payload(data) == encode(':usr'):
        serversock.sendto(encode_buffer(encode('%i users'%len(receivers)),speed), addr)

      elif decode_payload(data) == encode(':qtr'):
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        ntp_addr = socket.getaddrinfo(ntp_host, 123)[0][-1]
        ntp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
          ntp_sock.settimeout(1)
          ntp_res = ntp_sock.sendto(NTP_QUERY, ntp_addr)
          ntp_msg = ntp_sock.recv(48)
        finally:
          ntp_sock.close()
        val = struct.unpack("!I", ntp_msg[40:44])[0]
        val = val - NTP_DELTA
        tm = time.gmtime(val)
        serversock.sendto(encode_buffer(encode('%s' %time.strftime("%H%M",tm)),speed), addr)

      else:
        broadcast (data, client)
        receivers[client] = time.time()

    else:
      if decode_payload(data) == encode('hi') or decode_payload(data) == encode(':reconnect'):
        if (len(receivers) < MAX_CLIENTS):
          receivers[client] = time.time()
          if decode_payload(data) == encode('hi'):
          	welcome(client, speed)
        else:
          reject(client, speed)
          debug ("ERR: maximum clients reached")

      else:
        debug ("-unknown client, ignoring-")

  #except socket.timeout
  except OSError:
    # Send UDP keepalives
    for c in receivers.keys():
      ip,port = c.split(':')
      serversock.sendto(b'', addr)

  except (KeyboardInterrupt, SystemExit):
    serversock.close()
    break

  # clean clients list
  for c in receivers.copy().items():
    if c[1] + CLIENT_TIMEOUT < time.time():
      ip,port = c[0].split(':')
      serversock.sendto(encode_buffer(encode(':bye'),speed), addr)
      del receivers[c[0]]
      debug ("Removing expired client %s" % c[0])
