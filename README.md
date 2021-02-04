# sigbit
Morse code communication over ip networks

SigBit aims to provide a server client architecture implementing the MOPP Morse Over Packet Protocol for CW communications over ip networks.

The ESP_Server variant is designed to run on a ESP microcontroller board.
MOPP_Chat_server.py runs on a regular PC.

The script main.py implements a PC client and iambic keyer for use with an iambic paddle. The paddle can be connected to the PC using the serial / COM interface either buildt-in to the computer or via a USB to serial adapter.


# setup

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

### binary release packages

Simply download the binary package that suits your operating system and copy it to your desired location (e.e. ***/home/<username>/bin*** on linux or ***C:\Program Files\sigbit***)   

To run these binary packages, simply call them from a console window (type **cmd** on windows)

**current releases**

[sigbit-trx_linux_64_0.1.2.app](https://github.com/tuxintrouble/sigbit/blob/main/dist-bin/sigbit-trx_linux_64_0.1.2.app)
    
[sigbit-trx_win32_0.1.0.exe](https://github.com/tuxintrouble/sigbit/blob/main/dist-bin/sigbit-trx_win32_0.1.0.exe)

[sigbit-trx_win64_0.1.0.exe](https://github.com/tuxintrouble/sigbit/blob/main/dist-bin/sigbit-trx_win64_0.1.0.exe)

### source installation

SigBit runs on python3 and requires the following non-standard libraries:

- pyserial
- sounddevice
- appdirs
- numpy

The easiest way to obtain them is via pip3 install:

on linux run in a shell: 
	
	sudo python3 pip install pyserial sounddevice appdirs numpy


On linux you need to add your user to the group _dialout_

on linux run in a shell: 

	sudo adduser <your_user_name> dialout


# settings

Sigbit is configured through a config.ini file. The location on this file is depending on your operating system and it is created during the first startup of the application. 

SigBit uses the first detected serial port by default. If you use a USB to serial adapter, it is advised to have it plugged in during the first startup of SigBit, so it can detect the serial port and write it to the configfile. Otherwise, and in some other cases, you may have do adjust this setting to the correct serial port in the configfile, manually.

Comon values on linux are **/dev/ttyUSB0**, **/dev/ttyUSB1**, etc for USB adapters or **/devttyS0**, **/devttyS1**, etc. for ports on the mainboard.  

On windows it will be something like **COM1**, **COM2**, etc.
 

>
>On Linux, you will find the configuration file under: 
>
>	/home/<username>/.config/SigBitTRX/0.1  
>
>On Windows 7 it is under: 
>
>	C:\\Users\\<username>\\AppData\\Local\\DJ5SE\\SigBitTRX  
>
>On Mac it is:  
>
>	/Users/<username>/Library/Application Support/SigBitTRX  
>
  
You can edit the following variables to match your server IP or hostname and port, as well as the keyer speed in WPM and the side tone frequency in Hz:  

	server_url = morse.spdns.org  #or IP address of alternative server
	server_port = 7373
	keyer_speed = 18 #WPM
	serial_port = /dev/ttyUSB0 #serial port to use
	sidetone_freq = 550 #Hz
	autoreconnect = True #set to False if it causes problems with a server
	decode_cw = True  #currently not used



You can then launch the script "main.py" by running from a shell:
	
	python3 main.py


# usage
After launching main.py, you should hear a sidetone if you use your paddle. 

## connecting to a server

The code is sent to the server but will not be relayed, unless you register sending **HI** (.... ..) in morse code. The server will then respond sending ***WELCOME*** (.-- . .-.. -.-. --- -- .) and you will be able to receive transmissions from all other registered users and to send code to all other connected users. The code is sent automatically as soon as the end of a word is detected.

You are either disconnected by the server after 10 minutes of inactivity or you can disconnect by sending **:QRT** (---... --.- .-. -) in morse code. In either case the server will sign off sending ***BYE*** (-... -.-- .). If you have autoreconnect enabled, the client will automatically try to reconnect.

## server morse commands

There are some additional server commands, such as activating / deactivating echo mode for testing purposes by sending **:EM** (---... . --). The server will respond by sending you the current state, either ***ON*** (--- -.) or ***OFF*** (--- ..-. ..-.). 
Usually the sending user is excluded from receiving his / her own transmissions. In echo mode, own transmissions are sent back to the sending user as well. This is not suitable for actual communication, but may be helpfull for testing / debugging purposes. Please note that this is a server setting which affects all users.

When sending the command **:USR** (---... ..- ... .-.), the server will report the number of currently active users.

## client morse commands

> Note: some of the following commands may not have been implemented, yet

There are a couple of client commands:

**/QRS** (-..-. --.- .-. ...) decreases keyer speed one WPM slower, responds with current speed in WPM.

**/QRQ** (-..-. --.- .-. --.-) increases keyer speed one WPM, responds with current speed in WPM.

**/QTR** -..-. --.- - .-.) responds with the current utc time.

**/CMD** (-..-. -.-. -- -..) enter command mode, responds with **CMD?** (-.-. -- -.. ..--..), waits for a command to be entered. Command mode can be left by sending 4 or 8 dits.

In command mode: **SPEED** (... .--. . . -..), responds with ***SPEED?*** (... .--. . . -.. ..--..) allows to enter a new two digit keyer speed directely.

If a command or value is incorrect or not recognized, the keyer will respond with ***?*** (..--..)

# QSO practice

SigBit is designed to mimick real radio QSOs. There is not much of a user interface appart form your morse key and the sidetone. This means that you have to identify yourself with your callsign as if you where on the radio. Otherwise nobody will know who is talking to whom. You can identify in the same way as on radio by putting **recipientCallSign DE senderCallSign** at the beginning and the end of your transmissions.

It is good practice to hear for a while after connecting to be sure there is no  QSO that could be interrupted. Afterwards you should send a **QRL?** (--.- .-. .-.. ..--..) to ask whether the server is currently in use.  
If no one responds, you can call **CQ DE YourCallSign K** a couple of times to see if someone will answer you.

Since the code is transmitted word wise, it is important to wait for the other party to finish their transmission, and ending with **K** (-.-) or **KN** (-.- -.) indicating that they are ready to receive. 
