#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# configuration handling for SigBit application

import configparser, os, sys
from appdirs import AppDirs
import serial.tools.list_ports

DEBUG=False

def debug(caller,txt):
    if DEBUG:
        print(txt)


class AppConfig():

    def __init__(self, appname, author, version = None):
        
        dirs = AppDirs(appname, author, version)
        self.configdir = dirs.user_config_dir
        self.config_file_name = os.path.join(self.configdir,"config.ini")
        debug(self,self.config_file_name)
        self.config = configparser.ConfigParser()

        first_serial_port = ''
        if len(serial.tools.list_ports.comports()) > 0:
            first_serial_port = serial.tools.list_ports.comports()[0][0]
            
        self.config['DEFAULT'] = {
            'server_url' : 'morse.spdns.org',
            'server_port' : '7373',
            'keyer_speed' : '18',
            'serial_port' : first_serial_port,
            'sidetone_freq' : '550',
            'autoreconnect' : 'True',
            'decode_cw' : 'True'
            }
        self.load()


    def load(self):
        
        if os.path.exists(self.config_file_name):
            try:
                self.config.read(self.config_file_name)
            except Exception as err:
                print(err)
        else:
            
            #see if we have that path, if not create it
            if not os.path.exists(self.configdir):
                try:
                    os.makedirs(self.configdir)
                    debug(self.configdir, " created.")
                except Exception as err:
                    print(err)

            #copy defaulf configuration
            #self.config['USER'] = self.config['DEFAULT']

            try:
                with open(self.config_file_name, 'w') as configfile:
                    self.config.write(configfile)
                    debug("configuration saved to ",self.config_file_name)
            except Exception as err:
                print(err)

    def save(self):
        try:
            with open(self.config_file_name, 'w') as configfile:
                self.config.write(configfile)
        except Exception as err:
            print(err)

    def get(self, key):
        return self.config['DEFAULT'].get(key)

    def getint(self, key):
        return self.config['DEFAULT'].getint(key)

    def getboolean(self,key):
        return self.config['DEFAULT'].getboolean(key)

    def set(self, key, val):
        self.config['DEFAULT'][key] = str(val)

        
