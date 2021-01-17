# sigbit
Morse code communication over ip networks

SigBit aims to provide a server client architecture implementing the MOPP Morse Over Packet Protocol for CW communications over ip networks.

The ESP_Server variant is designed to run on a ESP microcontroller board.
MOPP_Chat_server.py runs on a regular PC.

The script main.py implements a PC client and iambic keyer for use with an iambic paddle. The paddle can be connected to the PC using the serial / COM interface either buildt-in to the computer or via a USB to serial adapter.


#setup

## hardware requirements

To interface your key to the computer, you can build a very simple adapter which connects the Pins 4, 6 and 8 t of a DB9 female connector to your paddle contacts via stereo socket or whatever your key requires.

>*DB9 – 9 Pin Serial Port Connection*
>
>| DB9 connector | purpose      | stereo connector |
>|---------------|--------------|------------------|
>| 6             | left paddle  | tip              |
>| 4             | common       | sleve            |
>| 8             | right paddle | ring             |


Besides the serial interface, you will need a soundcard for the tones and a network or internet connection.

## software installation

SigBit runs on python3 and requires the following non-standard libraries:

- pyserial
- sounddevice

The easiest way to obtain them is via pip3 install:

on linux run in a shell: 
	pip3 install pyserial sounddevice


You may have to change the _key_ settings in main.py to reflect your serial port.
	key = "/dev/ttyUSB0"

Comon values are /dev/ttyUSB0, /dev/ttyUSB1 or /devtty0, etc. 
On windows it will be something like COM1, COM2, etc.

On linux you need to add your user to the group _dialout_

on linux run in a shell: 
	sudo adduser <your_user_name> dialout

Edit the following variables to match your server IP or hostname and port:

	server_url = "morse.dyndnss.net" #this can also be a local IP address or hostname for your server
	server_port = 7373


You can then launch the script "main.py" by running from a shell:
	python3 main.py


# usage
After launching main.py, you should hear a sidetone if you use your paddle. 

## connecting to a server

The code is sent to the server but will not be relayed, unless you register sending **HI** (... ..) in morse code. The server will then respond sending ***WELCOME*** (.-- . .-.. -.-. --- -- .) and you will be able to receive transmissions from all other registered users and to send code to all other connected users. The code is sent automatically as soon as the end of a word is detected.

You are either disconnected by the server after 30 minutes of inactivity or you can disconnect by sending **:QRT** (---... --.- .-. -) in morse code. In either case the server will sign off sending ***BYE*** (-... -.-- .).

## server morse commands

There are some additional server commands, such as activating / deactivating echo mode for testing purposes by sending **:EM** (---... . --). The server will respond by sending you the current state, either ***ON*** (--- -.) or ***OFF*** (--- ..-. ..-.). 
Usually the sending user is excluded from receiving his / her own transmissions. In echo mode, own transmissions are sent back to the sending user as well. This is not suitable for actual communication, but may be helpfull for testing / debugging purposes. Please note that this is a server setting which affects all users.

When sending the command **:USR** (---... ..- ... .-.), the server will report the number of currently active users.

## client morse commands

> Note: some of the following commands may not have been implemented, yet

There are a couple of client commands:

**/QRS** (-..-. --.- .-. ...) decreases keyer speed one WPM slower, responds with current speed in WPM.


**/QRQ** (-..-. --.- .-. --.-) increases keyer speed one WPM, responds with current speed in WPM.

**/QTR** (---... --.- - .-.) responds with the current local time.

**/CMD** (---... -.-. -- -..) enter command mode, responds with **CMD?** (-.-. -- -.. ..--..), waits for a command to be entered. Command mode can be left by sending 4 or 8 dits.

In command mode: **SPEED** (... .--. . . -..), responds with ***SPEED?*** (... .--. . . -.. ..--..) allows to enter a new two digit keyer speed directely.

If a command or value is incorrect or not recognized, the keyer will respond with ***?*** (..--..)

# QSO practice

SigBit is designed to mimick real radio QSOs. There is not much of a user interface appart form your morse key and the sidetone. This means that you have to identify yourself with your callsign as if you where on the radio. Otherwise nobody will know who is talking to whom. You can identify in the same way as on radio by putting **recipientCallSign DE senderCallSign** at the beginning and the end of your transmissions.

It is good practice to hear for a while after connecting to be sure there is no  QSO that could be interrupted. Afterwards you should send a **QRL?** (--.- .-. .-.. ..--..) to ask whether the server is currently in use.  
If no one responds, you can call **CQ DE YourCallSign K** a couple of times to see if someone will answer you.

Since the code is transmitted word wise, it is important to wait for the other party to finish their transmission, and ending with **K** (-.-) or **KN** (-.- -.) indicating that they are ready to receive. 
