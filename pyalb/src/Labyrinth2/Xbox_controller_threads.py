# -*- coding: utf-8 -*-

from inputs import devices
from threading import Thread



def xbox_inputs_handler(sensibilities, event_handler) :
    stop = False
    activated = dict()

    gamepad = devices.gamepads[0]

    while not stop :
        xinput = gamepad.read()[0]
        if xinput.code == "BTN_SELECT" and xinput.state == 1:
            stop = True
        elif xinput.ev_type == 'Absolute' :
            if xinput.state > 0 :
                state = 1
            else :
                state = -1
                
            if abs(xinput.state) >= sensibilities[xinput.code] :

                if not activated.get(xinput.code + str(state), False) :
                    activated[xinput.code + str(state)] = True
                    event_handler(xinput, state, False)
                    
            elif activated.get(xinput.code + str(state), False) :
                activated[xinput.code + str(state)] = False
                event_handler(xinput, state, True)

        elif xinput.ev_type == 'Key' :
            event_handler(xinput, releasing=not xinput.state)


class ListeningThread(Thread) :

    def __init__(self, sensibilities, event_handler) :
        super().__init__()

        self.sensibilities = sensibilities
        self.event_handler = event_handler
        self.stop = False

    def run(self) :

        activated = dict()

        gamepad = devices.gamepads[0]

        while not self.stop :
            xinput = gamepad.read()[0]

            if xinput.ev_type == 'Absolute' :
                if xinput.state > 0 :
                    state = 1
                else :
                    state = -1
                    
                if abs(xinput.state) >= self.sensibilities[xinput.code] :

                    if not activated.get(xinput.code + str(state), False) :
                        activated[xinput.code + str(state)] = True
                        self.event_handler(xinput, state, False)
                        
                elif activated.get(xinput.code + str(state), False) :
                    activated[xinput.code + str(state)] = False
                    self.event_handler(xinput, state, True)

            elif xinput.ev_type == 'Key' :
                self.event_handler(xinput, releasing=not xinput.state)
