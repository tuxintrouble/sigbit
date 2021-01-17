#!/usr/local/bin/python3
#
# This file is part of the SigBit project
# https://github.com/tuxintrouble/sigbit
# Author: Sebastian Stetter, DJ5SE
# License: GNU GENERAL PUBLIC LICENSE Version 3
#
# implements morse code menu and actions


from util import ditlen, decode



class Action():
    """Implements an action for the commandfilter to execute based on current mode and user input"""
    def __init__(self,command, base_mode, target_mode, response, target_fn=None, args=None, arg_filter):
        
        self.command = command
        self.base_mode = base_mode
        self.target_mode = target_mode
        self.response = response

        self.target_fn = target_fn
        self.args = args
        self.arg_filter = arg_filter

####Example
actions.append(Action("/qsy", "idle", "cmd_qsy","qrg?",target_fn=None, args=None,arg_filter=None))
actions.append("enter_mode", "cmd_qsy", "idle","r new qrg %i",target_fn=set_qrg, args=buffer,arg_filter=qrg_filter)



class ActionFilter():

command base_mode   target_mode target_func arg response        arg_filter_func
//      "idle"      "cmd"       None        None   "cmd?"       None
#"speed" "cmd"       "idle"      set_wpm     buffer "%i WPM" %!  speed_arg_filter(arg)



mode = "idle" #idle, recv, send, cmd, cmd_enter_speed, cmd_enter_channe



#filter_action(decode(word_buffer)) #do soemthing with Wordbuffer before we clear it

def filter_action(text):
        '''filters text to execute action base on mode and command'''
        global wpm
        global mode
        global channel

        text = text.strip()
        #print(mode)

        if mode != "idle" and (text == "eeee" or text =="eeeeeeee"):
                print("r exit command")
                mode = "idle"
        
        elif mode =="idle":
                ##the commands menu
                if text == "//":
                        print("cmd?")
                        mode = "cmd"
                        return

                elif text == "/qrg":
                        print("ch %i" %channel)
                        return
                elif text == "/qsy":
                        print("qrg?")
                        mode = "cmd_qsy"
                        return
                elif text == "/qrs":
                        if wpm > 8:
                                wpm -= 1
                        print("speed %i wpm" %wpm)
                        return
                elif text == "/qrq":
                        if wpm < 30:
                                wpm += 1
                        print("speed %i wpm" %wpm)
                        return
                elif text == "/speed":
                        print("speed?")
                        mode = "cmd_speed"
                        return
                elif text == "/qtr":
                        #tell current time
                        print("qtr " +datetime.now().strftime("%H %M"))
                        return
                else:
                        #send text via mopp
                        print(">>>"+text)
                        return
        if mode == "cmd_speed":
                if text.isnumeric() and 7 < int(text) < 30:
                        wpm = int(text)
                        print("r speed %i wpm" %wpm)
                        mode = "idle"
                else:
                        print("agn speed ?")

        elif mode == "cmd_qsy":
                if text.isnumeric() and (0 < int(text) <= 10):
                        channel = int(text)
                        print("r qsy %i" %channel)
                        mode = "idle"
                else:
                        print("agn qrg?")
                        
        elif mode == "cmd":
                if text == "?":
                        print("comands: speed")

                elif text == "speed":
                        print("%i wpm" %wpm)
                        print("new speed?")
                        mode = "cmd_speed"
                else:
                        print("agn cmd?")




    
