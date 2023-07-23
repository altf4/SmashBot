#!/usr/bin/python3
import socket
from collections import deque
from typing import Tuple, Optional

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

ITEMS = {
    "capsule": b"\x00",
    "box": b"\x01",
    "barrel": b"\x02",
    "egg": b"\x03",
    "party_ball": b"\x04",
    "barrel_cannon": b"\x05",
    "bob_omb": b"\x06",
    "mr_saturn": b"\x07",
    "heart_container": b"\x08",
    "maxim_tomato": b"\x09",
    "star_man": b"\x0A",
    "homerun_bat": b"\x0B",
    "beam_sword": b"\x0C",
    "parasol": b"\x0D",
    "green_shell": b"\x0E",
    "red_shell": b"\x0F",
    "ray_gun": b"\x10",
    "freezie": b"\x11",
    "food": b"\x12",
    "proxy_mine": b"\x13",
    "flipper": b"\x14",
    "super_scope": b"\x15",
    "star_rod": b"\x16",
    "lips_stick": b"\x17",
    "fan": b"\x18",
    "fire_flower": b"\x19",
    "super_mushroom": b"\x1A",
    "mini_mushroom": b"\x1B",
    "hammer": b"\x1C",
    "warp_star": b"\x1D",
    "screw_attack": b"\x1E",
    "bunny_hood": b"\x1F",
    "metal_box": b"\x20",
    "cloaking_device": b"\x21",
    "pokeball": b"\x22",
    # SPECIAL
    "yoshi_egg": b"\x2A",
    "goomba": b"\x2B",
    "redead": b"\x2C",
    "octorok": b"\x2D",
    "ottosea": b"\x2E",
    "stone": b"\x2F"
}

MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

currentlySendingItem: Optional[bytes] = None
itemSendQueue = deque([])

def enqueueItem(item: bytes):
    """Put a new item into the queue"""
    global itemSendQueue
    itemSendQueue.append(item)

def enqueueItemIndex(item: str) -> str:
    if item not in ITEMS:
        return 'failPermanent'
    enqueueItem(ITEMS[item])
    return 'success'

def popItem():
    """Pop an item from the queue and into the current sending slot"""
    global currentlySendingItem
    global itemSendQueue
    if len(itemSendQueue) > 0 and currentlySendingItem is None:
        currentlySendingItem = itemSendQueue.pop()

def checkItemSpawn(itemsList):
    """Check if the current sending item has spawned, dequeuing if true"""
    global currentlySendingItem
    if currentlySendingItem is None:
        return False
    for item in itemsList:
        itemInt = int.from_bytes(currentlySendingItem, byteorder='big')
        if item.type.value == itemInt:
            if item.frame >= 1399:
                currentlySendingItem = None
                popItem()
                return True
    return False

def trySendItem(itemsList):
    """Send an item send command. But it might fail."""
    global currentlySendingItem
    global sock
    if currentlySendingItem is not None and len(itemsList) < 10:
        for i in range(10):
            MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"
            message = MARKER + b"\x00" + currentlySendingItem + (b"\x00" * 23)
            sock.sendto(message, (UDP_IP, UDP_PORT))


if __name__ == "__main__":
    print(enqueueItemIndex("goomba"))
