import socket
import pygame
import enum
import time
import cv2
import requests
import numpy as np
import threading
import json


car_ip = None
car_port = 25006

feed_port = 8001
feed_url = "/stream.mjpg"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



def sendMsg(action, value):
    data = {}
    data["action"] = action
    data["value"] = value    

    client.sendto(str.encode(json.dumps(data)), (car_ip, car_port))

                  
def videoLoop():    
    r = requests.get('http://' + str(car_ip) + ':' + str(feed_port) + feed_url, stream=True)
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
                val = int((round(event.value,2) +1) * 17 + 990)
                sendMsg("Backwards", val)
                print(val)   
            elif event.type == pygame.JOYAXISMOTION and event.axis == 5:
                val = int((round(event.value,2) + 1) * 17 + 990)
                sendMsg("Forward", val)
                print(val)
            elif event.type == pygame.JOYHATMOTION:
                if event.value[0] == 0:
                    sendMsg("X-Idle",0)
                elif event.value[0] == -1:
                    sendMsg("Left",1024)
                elif event.value[0] == 1:
                    sendMsg("Right",1024)
            elif event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    print("Forward")
                    sendMsg("Forward",1024)
                elif event.key == pygame.K_DOWN:
                    print("Backwards")
                    sendMsg("Backwards",1024)
                elif event.key == pygame.K_RIGHT:
                    print("Right")
                    sendMsg("Right",1024)
                elif event.key == pygame.K_LEFT:
                    print("Left")
                    sendMsg("Left",1024)
                elif event.key == pygame.K_q:
                    try:
                        controller.quit()
                    except:
                        pass
                    return
            elif event.type == pygame.KEYUP and (event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT):
                print("X-Idle")
                sendMsg("X-Idle",0)
            elif event.type == pygame.KEYUP and (event.key == pygame.K_UP or event.key == pygame.K_DOWN):
                print("Y-Idle")
                sendMsg("Y-Idle",1024)


def main():
    global car_ip
    car_ip = input("[*] Enter IP of Hugo: ")
    feed = input("[*] Start video feed? [y/n]: ")
    if feed == 'y':
        thread = threading.Thread(target=videoLoop)                
        thread.start()    
    controlLoop()


if __name__ == "__main__":
    main()
