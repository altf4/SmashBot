#!/usr/bin/python3
import socket

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
    client.connect("crowdcontrol_socket.fifo")
    for i in range(5):
        client.send(b"\x06")
