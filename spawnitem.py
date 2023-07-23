#!/usr/bin/python3
import socket
from collections import deque
from typing import Optional, Deque

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

ITEMS = {
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

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

currentlySendingItem: Optional[int] = None
itemSendQueue: Deque[int] = deque([])

def enqueueItem(item: int):
    """Put a new item into the queue"""
    global itemSendQueue
    itemSendQueue.append(item)

def popItem():
    """Pop an item from the queue and into the current sending slot"""
    global currentlySendingItem
    global itemSendQueue
    if len(itemSendQueue) > 0 and currentlySendingItem is None:
        currentlySendingItem = itemSendQueue.pop()

def checkItemSpawn(itemsList) -> bool:
    """Check if the current sending item has spawned, dequeuing if true"""
    global currentlySendingItem
    if currentlySendingItem is None:
        return False
    for item in itemsList:
        if item.type.value == currentlySendingItem and item.frame >= 1399:
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
            message = MARKER + b"\x00" + int.to_bytes(currentlySendingItem, 1, 'big') + (b"\x00" * 23)
            sock.sendto(message, (UDP_IP, UDP_PORT))
