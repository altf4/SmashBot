#!/usr/bin/python3
import socket
import argparse

from spawnitem import getItemBytes

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--bobombs', '-b', action='store_true')

args = parser.parse_args()

with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
    client.connect("crowdcontrol_socket.fifo")
    if args.bobombs:
        for i in range(25):
            client.send(getItemBytes("bob_omb"))
    else:
        client.send(getItemBytes("yoshi_egg"))
        client.send(getItemBytes("goomba"))
        client.send(getItemBytes("redead"))
        client.send(getItemBytes("octorok"))
        client.send(getItemBytes("ottosea"))
