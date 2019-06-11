import socket
import wiringpi
import time
import json


""" Pin definitions """

FORWARD = 13
BACKWARD = 12
RIGHT = 21
LEFT = 20
STATUS = 26

""" General definitions """
PWM = 2 
ON = 1
OFF = 0

LISTEN_PORT = 25006
LOCALHOST = "0.0.0.0"

def initialize_pins():
    """ Initialize the pins needed for vehicle control. """
    
    # Set wiringPi to use GPIO numbers
    wiringpi.wiringPiSetupGpio()

    # Set pins GPIO20-21 to Output-mode
    wiringpi.pinMode(RIGHT,ON) 
    wiringpi.pinMode(LEFT,ON) 

    # Set pins GPIO20-21 Low
    wiringpi.digitalWrite(RIGHT,OFF)
    wiringpi.digitalWrite(LEFT,OFF)

    # Set pins GPIO12-13 to Alternative mode (PWM)
    wiringpi.pinMode(FORWARD,PWM)      
    wiringpi.pinMode(BACKWARD,PWM)

    # Set GPIO26 as output (Status light)
    wiringpi.PinMode(STATUS,ON)

    # Set GPIO26 Low
    wiringpi.digitalWrite(STATUS,OFF)



def set_status_light(status):
        wiringpi.digitalWrite(STATUS, status)
        
def turn_right():
    """ Turn the vehicle right """
    wiringpi.digitalWrite(LEFT,OFF)
    wiringpi.digitalWrite(RIGHT,ON)

def turn_left():
    """ Turn the vehicle left """
    wiringpi.digitalWrite(LEFT,ON) 
    wiringpi.digitalWrite(RIGHT,OFF)



def engine_forward(speed = 0):
    """
    Moves the engine forward with a specified speed.

    Keyword arguments:
    speed -- The speed of which the vehicle should move (default 0)
             Note that Hugo only has interval between 990-1024
    """
    
    if speed <= 990:
        speed = 0
    elif speed > 1024:
        speed = 1024

    wiringpi.pwmWrite(FORWARD, speed)  
    wiringpi.pwmWrite(BACKWARD, OFF)
        
def engine_backwards(speed = 0):
    """
    Moves the engine backwards with a specified speed.

    Args:
        speed: The speed of which the vehicle should move (default 0)
               Note that Hugo only has interval between 990-1024
    """
    
    if speed <= 990:
        speed = 0
    elif speed > 1024:
        speed = 1024
        

    wiringpi.pwmWrite(BACKWORD, speed)
    wiringpi.pwmWrite(FORWARD, OFF)


def x_idle():
    """ Sets the turn-engine to idle (X-axis) """
    wiringpi.digitalWrite(LEFT,OFF)
    wiringpi.digitalWrite(RIGHT,OFF)

def y_idle():
    """ Sets the moving-engine to idle (Y-axis) """
    wiringpi.pwmWrite(FOORWARD,OFF)
    wiringpi.pwmWrite(BACKWARD,OFF)
        
def all_idle():
    """ Sets all engines idle """
    wiringpi.digitalWrite(LEFT,OFF)
    wiringpi.digitalWrite(RIGHT,OFF)
    wiringpi.pwmWrite(FORWARD, OFF)
    wiringpi.pwmWrite(BACKWARD, OFF)
    
def handleCommand(command):
    """
    Handle incomming command
    
    Args:
        command: command in JSON-format.
                 Must contain an action
                 Can contain a value
    """
    try:
        data = json.loads(str(command.decode("utf-8")))
        if data['action'] == None:
            raise Exception("No action")
    except Exception as e:
        print("[-] Invalid / Non parseable command, ignoring.")
        return

    if data['action'] == 'Forward':
        if data["value"] == None:
            data["value"] == 0
        engine_forward(data["value"])
    elif data["action"] == "Backwards":
        if data["value"] == None:
            data["value"] == 0
        engine_backwards(data["value"])
    elif data["action"] == "Right":
        turn_right()
    elif data["action"] == "Left":
        turn_left()
    elif data["action"] == "Y-Idle":
        y_idle()
    elif data["action"] == "X-Idle":
        x_idle()
    else:
        all_idle()


def initialize_server():
    """ Initializes UDP Serverlistener """
    buffersize = 1024
    
    print("[*] Starting UDP Server on port {0}...".format(listen_port))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((LOCALHOST,LISTEN_PORT))

    print("[+] Done")
    set_status_light(ON)
    while 1:
        data, addr = s.recvfrom(buffersize)
        handleCommand(data)
        


if __name__ == "__main__":
    initialize_pins()
    initialize_server()
                
