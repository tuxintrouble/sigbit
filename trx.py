#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# UDP 'Transceiver' for the client side


import socket, time, os
from math import ceil
from util import morse, zfill, ljust

DEBUG=1
def debug(s):
    if DEBUG:
        print(s)


class TRX():
        
    def __init__(self,buzzer, url=('0.0.0.0',7374),timeout=0):
        self.buzzer = buzzer
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.connect(url)
        self.sock.settimeout(timeout)

        self.protocol_version = 1
        self.serial = 1
        
        if not os.uname()[0].startswith("esp"): #disable for ESP systems
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)


    def sendto(self, data, url):
        try:
            self.sock.sendto(data,url)
        except:
            self.buzzer.play_text("error")
            
    def recv(self):
        data=None
        try:
            data = self.sock.recv(64)
        except:
            pass
        #return[decode_header(data),decode_payload(data)]
        return data

      
    def encode_buffer(self,buffer,wpm):
        '''creates an bytes for sending throught a socket'''
        #buffer is a list of elements as strings as produced by the keyer

        """Protocol description:
        This may be compatible with the morserino protocol


        protocolversion: 2 bits
        serial number: 6 bits
        morse speed: 6 bits
        text: variable length of 2bit characters

        01 = dit
        10 = dah
        00 = End of Character
        11 = End of Word
        """
        #create 14 bit header
        m = zfill(bin(self.protocol_version)[2:],2) #2bits for protocol_version
        m += zfill(bin(self.serial)[2:],6) #6bits for serial number
        m += zfill(bin(wpm)[2:],6) #6bits for words per minute

        #add payload
        for el in buffer:
            m += el

        m = ljust(m,int(8*ceil(len(m)/8.0)),'0') #fill in incomplete byte
        res = ''
        for i in range(0, len(m),8):
            res += chr(int(m[i:i+8],2)) #convert 8bit chunks to integers and the to characters
        self.serial +=1

        return res.encode('utf-8') #convert string of characters to bytes


    def decode_header(self, unicodestring):
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

    def decode_payload(self, unicodestring):
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


if __name__ == "__main__":
    buffer = ['10','01','10','01','00','10','10','01','10','11']
    wpm = 20
    trx = TRX(None)
    data = trx.encode_buffer(buffer,20)
    header = trx.decode_header(data)[2]
    recvbuffer = trx.decode_payload(data)
    
    
    
