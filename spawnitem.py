#!/usr/bin/python3
import socket

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

CAPSULE = b"\x00"
BOX = b"\x01"
BARREL = b"\x02"
EGG = b"\x03"
PARTY_BALL = b"\x04"
BARREL_CANNON = b"\x05"
BOB_OMB = b"\x06"
MR_SATURN = b"\x07"
HEART_CONTAINER = b"\x08"
MAXIM_TOMATO = b"\x09"
STAR_MAN = b"\x0A"
HOMERUN_BAT = b"\x0B"
BEAM_SWORD = b"\x0C"
PARASOL = b"\x0D"
GREEN_SHELL = b"\x0E"
RED_SHELL = b"\x0F"
RAY_GUN = b"\x10"
FREEZIE = b"\x11"
FOOD = b"\x12"
PROXY_MINE = b"\x13"
FLIPPER = b"\x14"
SUPER_SCOPE = b"\x15"
STAR_ROD = b"\x16"
LIPS_STICK = b"\x17"
FAN = b"\x18"
FIRE_FLOWER = b"\x19"
SUPER_MUSHROOM = b"\x1A"
MINI_MUSHROOM = b"\x1B"
HAMMER = b"\x1C"
WARP_STAR = b"\x1D"
SCREW_ATTACK = b"\x1E"
BUNNY_HOOD = b"\x1F"
METAL_BOX = b"\x20"
CLOAKING_DEVICE = b"\x21"
POKEBALL = b"\x22"

# SPECIAL
YOSHI_EGG = b"\x2A"
GOOMBA = b"\x2B"
REDEAD = b"\x2C"
OCTOROK = b"\x2D"
OTTOSEA = b"\x2E"
STONE = b"\x2F"


# XXX: Change the item here to spawn the item
selected_item = GOOMBA

MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

for i in range(10):
    message = MARKER + b"\x00" + selected_item + (b"\x00" * 23)
    sock.sendto(message, (UDP_IP, UDP_PORT))