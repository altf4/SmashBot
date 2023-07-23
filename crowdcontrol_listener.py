#!/usr/bin/python3
import socket
import argparse

from spawnitem import ITEMS

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--bobombs', '-b', action='store_true')

args = parser.parse_args()

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
    client.connect("crowdcontrol_socket.fifo")
    if args.bobombs:
        for i in range(25):
            client.send(ITEMS["bob_omb"])
    else:
        client.send(ITEMS["yoshi_egg"])
        client.send(ITEMS["goomba"])
        client.send(ITEMS["redead"])
        client.send(ITEMS["octorok"])
        client.send(ITEMS["ottosea"])
