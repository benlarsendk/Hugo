import socket
import wiringpi
import time
import json

def initialize_pins():
    """ Initialize the pins needed for vehicle control. """
    
    # Set wiringPi to use GPIO numbers
    wiringpi.wiringPiSetupGpio()

    # Set pins GPIO20-21 to Output-mode
    wiringpi.pinMode(20,1) 
    wiringpi.pinMode(21,1) 

    # Set pins GPIO20-21 Low
    wiringpi.digitalWrite(20,0)
    wiringpi.digitalWrite(21,0)

    # Set pins GPIO12-13 to Alternative mode (PWM)
    wiringpi.pinMode(13,2)      
    wiringpi.pinMode(12,2)

def turn_right():
    """ Turn the vehicle right """
    wiringpi.digitalWrite(20,0)
    wiringpi.digitalWrite(21,1)

def turn_left():
    """ Turn the vehicle left """
    wiringpi.digitalWrite(20,1) 
    wiringpi.digitalWrite(21,0)



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

    wiringpi.pwmWrite(13, speed)  
    wiringpi.pwmWrite(12, 0)
        
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
        

    wiringpi.pwmWrite(12, speed)
    wiringpi.pwmWrite(13, 0)


def x_idle():
    """ Sets the turn-engine to idle (X-axis) """
    wiringpi.digitalWrite(20,0)
    wiringpi.digitalWrite(21,0)

def y_idle():
    """ Sets the moving-engine to idle (Y-axis) """
    wiringpi.pwmWrite(13,0)
    wiringpi.pwmWrite(12,0)
        
def all_idle():
    """ Sets all engines idle """
    wiringpi.digitalWrite(20,0)
    wiringpi.digitalWrite(21,0)
    wiringpi.pwmWrite(13, 0)
    wiringpi.pwmWrite(12, 0)
    
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
    listen_port = 25006
    localhost = "0.0.0.0"
    buffersize = 1024
    
    print("[*] Starting UDP Server on port {0}...".format(listen_port))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((localhost,listen_port))

    print("[+] Done")

    while 1:
        data, addr = s.recvfrom(buffersize)
        handleCommand(data)
        


if __name__ == "__main__":
    initialize_pins()
    initialize_server()
                
