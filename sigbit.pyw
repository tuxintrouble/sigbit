#!/usr/bin/python

__version__ = "1.0"

import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports

class MainWindow():

    def __init__(self):

        #get a list of all available comports
        self.comports = [ p[0] for p in serial.tools.list_ports.comports()]

        self.root = tk.Tk()
        self.root.title("SigBitTRX %s" %__version__)
        self.canvas = tk.Canvas(self.root)
        self.canvas = tk.Canvas(self.root,width=600, height=300)
        self.canvas.grid(columnspan=4)

        self.lbl_port = tk.Label(self.root,text="serial port")
        self.lbl_port.grid(column=0,row=0)
        self.cb_ports = ttk.Combobox(self.root,values=self.comports)
        self.cb_ports.grid(column=1,row=0)

        self.lbl_host = tk.Label(self.root,text="host")
        self.lbl_host.grid(column=0,row=1)
        self.host_string=tk.StringVar() #
        self.ent_host= tk.Entry(self.root,width=30,textvariable=self.host_string)
        self.ent_host.grid(column=1,row=1)

        self.lbl_port = tk.Label(self.root,text="port")
        self.lbl_port.grid(column=2, row=1)
        self.port_int = tk.IntVar() #
        self.ent_port = tk.Entry(self.root,width=5,textvariable=self.port_int)
        self.ent_port.grid(column=4, row=1)

        self.lbl_speed = tk.Label(self.root,text="speed")
        self.lbl_speed.grid(column=0, row = 2)
        self.speed_int = tk.IntVar() #
        self.sc_speed = tk.Scale(self.root,
                                 orient="horizontal", resolution=1,from_=5, to=35 )
        self.sc_speed.grid(column = 1, row=2)

        self.lbl_tone = tk.Label(self.root,text = "tone")
        self.lbl_tone.grid(column=2, row=2)
        self.tone_int = tk.IntVar() #
        self.sc_tone= tk.Scale(self.root, orient="horizontal", resolution=1,from_=100, to=800 )
        self.sc_tone.grid(column = 4, row=2)

        self.showText_int = tk.IntVar()
        self.cb_showText = tk.Checkbutton(self.root, variable = self.showText_int, text="show messages")
        self.cb_showText.grid(columnspan=2,column=0,row=3)
        self.showText_int.set(1)

        self.txt_messages = tk.Text(self.root)
        self.txt_messages.grid(columnspan=5,column=0,row=4)
        self.txt_messages.configure(state='disabled')

        self.root.mainloop()

    def update_ui(self):
        self.cb_ports.set("/dev/null")
        self.host_string("morse.spdns.org")
        self.port_int.set(7373)
        self.tone_int.set(650)
        self.speed_int(25)

    def add_message(self, message):
        if self.showText_int.get() == 1:
            self.txt_messages.insert("end",message)
        
        


if __name__ == "__main__":
    mw = MainWindow()
    #mw.update_ui()
    mw.add_message("One\n")
    mw.add_message("Two\n")
