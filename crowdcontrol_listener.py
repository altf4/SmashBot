#!/usr/bin/python3
import socket
import argparse
from collections import deque
import os
import time
from typing import Dict, Deque

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--bobombs', '-b', action='store_true')

args = parser.parse_args()

ITEMS: Dict[str, int] = {
    "capsule": 0x00,
    "box": 0x01,
    "barrel": 0x02,
    "egg": 0x03,
    "party_ball": 0x04,
    "barrel_cannon": 0x05,
    "bob_omb": 0x06,
    "mr_saturn": 0x07,
    "heart_container": 0x08,
    "maxim_tomato": 0x09,
    "star_man": 0x0A,
    "homerun_bat": 0x0B,
    "beam_sword": 0x0C,
    "parasol": 0x0D,
    "green_shell": 0x0E,
    "red_shell": 0x0F,
    "ray_gun": 0x10,
    "freezie": 0x11,
    "food": 0x12,
    "proxy_mine": 0x13,
    "flipper": 0x14,
    "super_scope": 0x15,
    "star_rod": 0x16,
    "lips_stick": 0x17,
    "fan": 0x18,
    "fire_flower": 0x19,
    "super_mushroom": 0x1A,
    "mini_mushroom": 0x1B,
    "hammer": 0x1C,
    "warp_star": 0x1D,
    "screw_attack": 0x1E,
    "bunny_hood": 0x1F,
    "metal_box": 0x20,
    "cloaking_device": 0x21,
    "pokeball": 0x22,
    # SPECIAL
    "yoshi_egg": 0x2A,
    "goomba": 0x2B,
    "redead": 0x2C,
    "octorok": 0x2D,
    "ottosea": 0x2E,
    "stone": 0x2F
}

MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def asBytes(item: int) -> bytes:
    return int.to_bytes(item, 1, 'big')

def getItemInt(index: str) -> int:
    return ITEMS[index]

def getItemBytes(index: str) -> bytes:
    return asBytes(getItemInt(index))

def trySpawnItem(item: bytes):
    for i in range(10):
        message = MARKER + b"\x00" + item + (b"\x00" * 23)
        udpSock.sendto(message, (UDP_IP, UDP_PORT))

def trySpawnItemInt(item: int):
    trySpawnItem(asBytes(item))

def trySpawnItemName(name: str):
    trySpawnItem(getItemBytes(name))

ccSocket = os.open("crowdcontrol_socket.fifo", os.O_RDONLY | os.O_NONBLOCK)

if __name__ == "__main__":
    itemSendQueue: Deque[bytes] = deque([])

    # TODO: getItemBytes

    if args.bobombs:
        for i in range(90):
            itemSendQueue.append(getItemBytes("bob_omb"))
    else:
        itemSendQueue.append(getItemBytes("yoshi_egg"))
        itemSendQueue.append(getItemBytes("goomba"))
        itemSendQueue.append(getItemBytes("redead"))
        itemSendQueue.append(getItemBytes("octorok"))
        itemSendQueue.append(getItemBytes("ottosea"))

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
        