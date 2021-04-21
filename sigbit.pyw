#!/usr/bin/python

__version__ = "1.0"

import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports

#get a list of all available comports
comports = [ p[0] for p in serial.tools.list_ports.comports()]

root = tk.Tk()
root.title("SigBitTRX %s" %__version__)
canvas = tk.Canvas(root,width=600, height=300)
canvas.grid(columnspan=4)

lbl_port = tk.Label(root,text="serial port")
lbl_port.grid(column=0,row=0)
cb_ports = ttk.Combobox(root,values=comports)
cb_ports.grid(column=1,row=0)

lbl_host = tk.Label(root,text="host")
lbl_host.grid(column=0,row=1)
host_string=tk.StringVar()
ent_host= tk.Entry(root,width=30,textvariable=host_string)
ent_host.grid(column=1,row=1)

lbl_port = tk.Label(root,text="port")
lbl_port.grid(column=2, row=1)
port_int = tk.IntVar()
ent_port = tk.Entry(root,width=5,textvariable=port_int)
ent_port.grid(column=4, row=1)

lbl_speed = tk.Label(root,text="speed")
lbl_speed.grid(column=0, row = 2)
sc_speed = tk.Scale(root, orient="horizontal", resolution=1,from_=5, to=35 )
sc_speed.grid(column = 1, row=2)

lbl_tone = tk.Label(root,text = "tone")
lbl_tone.grid(column=2, row=2)
sc_tone= tk.Scale(root, orient="horizontal", resolution=1,from_=100, to=800 )
sc_tone.grid(column = 4, row=2)

def show_message_window():
    print("I'd prefer not to.")

btn = tk.Button(root,text="show messages", command = lambda:show_message_window())
btn.grid(columnspan=2,column=0,row=3)

root.mainloop()
