#!/usr/bin/python3
import socket
import argparse
from collections import deque
import os
import time

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--bobombs', '-b', action='store_true')

args = parser.parse_args()

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def trySpawnItem(item):
    for i in range(10):
        MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"
        message = MARKER + b"\x00" + item + (b"\x00" * 23)
        udpSock.sendto(message, (UDP_IP, UDP_PORT))

ccSocket = os.open("crowdcontrol_socket.fifo", os.O_RDONLY | os.O_NONBLOCK)

itemSendQueue = deque([])

if args.bobombs:
    for i in range(90):
        itemSendQueue.append(b"\x06")
else:
    itemSendQueue.append(b"\x2A")
    itemSendQueue.append(b"\x2B")
    itemSendQueue.append(b"\x2C")
    itemSendQueue.append(b"\x2D")
    itemSendQueue.append(b"\x2E")

item = None
gameisFull = False

while len(itemSendQueue) > 0:
    print(len(itemSendQueue), "left")
    item = itemSendQueue.pop()
    spawned = False
    tryCounter = 0
    while not spawned and tryCounter < 5:
        end = time.time()
        # Keep trying to spawn the item until we get the signal that it spawned
        # XXX TODO: Add some random delay here. As much as you need. 
        if not gameisFull:
            trySpawnItem(item)
            print("Try to spawn:", item)
            tryCounter += 1
        time.sleep(0.017 * 4)
        try:
            while True:
                datagram = os.read(ccSocket, 1)
                if datagram == item:
                    spawned = True
                    print("SPAWNED", datagram)
                if datagram == b'\xFF':
                    gameisFull = True
                if datagram == b'\xFE':
                    gameisFull = False
        except BlockingIOError as ex:
            pass
        