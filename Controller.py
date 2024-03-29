import socket
import pygame
import enum
import time
import cv2
import requests
import numpy as np
import threading
import json


CAR_IP = None
CAR_PORT = 25006
FEED_PORT = 8001
FEED_URL = "/stream.mjpg"
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def sendMsg(action, value=None):
    """
    Sends a message to the vehicle
    Args:
        action: The action to be taken
        value: The value associated with that action, if needed (default None)
    """
    data = {}
    data["action"] = action
    data["value"] = value

    client.sendto(str.encode(json.dumps(data)), (CAR_IP, CAR_PORT))


def videoLoop():
    """ Starts the videofeed """
    url = "http://{0}:{1}{2}".format(CAR_IP, FEED_PORT, FEED_URL)
    r = requests.get(url, stream=True)
    if(r.status_code == 200):
        bytesz = bytes()
        for chunk in r.iter_content(chunk_size=1024):
            bytesz += chunk
            a = bytesz.find(b'\xff\xd8')
            b = bytesz.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytesz[a:b+2]
                bytesz = bytesz[b+2:]
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                cv2.imshow('i', i)
                if cv2.waitKey(1) == 27:
                    exit(0)
    else:
        print("[-] Received unexpected status code {}".format(r.status_code))


def controlLoop():
    """ Starts the control loop """
    print("[*] Initializing control-system")

    controller = None
    pygame.init()
    try:
        pygame.joystick.init()
        controller = pygame.joystick.Joystick(0)
        controller.init()
    except:
        print("[-] Controller not connected\n[*] Keyboard only")
    screen = pygame.display.set_mode((640, 480))
    print("[+] Control-system online\n[*] Press 'q' to quit")
    while True:
        pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION and event.axis == 2:
                val = int((round(event.value, 2) + 1) * 17 + 990)
                sendMsg("Backwards", val)
                print(val)
            elif event.type == pygame.JOYAXISMOTION and event.axis == 5:
                val = int((round(event.value, 2) + 1) * 17 + 990)
                sendMsg("Forward", val)
                print(val)
            elif event.type == pygame.JOYHATMOTION:
                if event.value[0] == 0:
                    sendMsg("X-Idle", 0)
                elif event.value[0] == -1:
                    sendMsg("Left", 1024)
                elif event.value[0] == 1:
                    sendMsg("Right", 1024)
            elif event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("Forward")
                    sendMsg("Forward", 1024)
                elif event.key == pygame.K_DOWN:
                    print("Backwards")
                    sendMsg("Backwards", 1024)
                elif event.key == pygame.K_RIGHT:
                    print("Right")
                    sendMsg("Right", 1024)
                elif event.key == pygame.K_LEFT:
                    print("Left")
                    sendMsg("Left", 1024)
                elif event.key == pygame.K_q:
                    try:
                        controller.quit()
                    except:
                        pass
                    return
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT):
                    print("X-Idle")
                    sendMsg("X-Idle", 0)
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_UP or event.key == pygame.K_DOWN):
                    print("Y-Idle")
                    sendMsg("Y-Idle", 1024)


def main():
    global CAR_IP
    CAR_IP = input("[*] Enter IP of Hugo: ")
    if input("[*] Start video feed? [y/n]: ") == 'y':
        thread = threading.Thread(target=videoLoop)
        thread.start()
    controlLoop()

if __name__ == "__main__":
    main()
