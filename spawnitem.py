#!/usr/bin/python3
import socket

UDP_IP = "192.168.0.205"
UDP_PORT = 55558

CAPSULE = b"\x00"
BOX = b"\x01"
BARREL = b"\x02"
EGG = b"\x03"
PARTY_BALL = b"\x04"
BOB_OMB = b"\x06"
BEAM_SWORD = b"\x0C"
GOOMBA = b"\x2B"

# XXX: Change the item here to spawn the item
selected_item = GOOMBA

MARKER = b"\x12\x34\x56\x78" + b"\x00\x00\x00"

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

for i in range(10):
    message = MARKER + b"\x00" + selected_item + (b"\x00" * 23)
    sock.sendto(message, (UDP_IP, UDP_PORT))
