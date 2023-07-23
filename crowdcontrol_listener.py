#!/usr/bin/python3
import socket
import argparse

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--bobombs', '-b', action='store_true')

args = parser.parse_args()

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
    client.connect("crowdcontrol_socket.fifo")
    if args.bobombs:
        for i in range(25):
            client.send(b"\x06")
    else:
        client.send(b"\x2A")
        client.send(b"\x2B")
        client.send(b"\x2C")
        client.send(b"\x2D")
        client.send(b"\x2E")
