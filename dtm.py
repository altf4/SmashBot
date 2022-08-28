#!/usr/bin/env python3
import struct
import sys

def read_header(data):
    magic, = struct.unpack('<4s', data[:0x4])
    if magic != b'DTM\x1a':
        raise RuntimeError('Bad movie magic')
    header = {'magic': magic}
    keys = ('Game ID', 'Wii Game', 'Controllers', 'SaveState', 'VI count', 'Input Count', 'Lag Count',
            'Reserved1', 'Rerecord Count', 'Author', 'Video Backend', 'Audio Emulator', 'MD5 Hash',
            'Start Time', 'Saved Config', 'Idle Skipping', 'Dual Core', 'Progressive Scan', 'DSP HLE',
            'Fast Disc', 'CPU Core', 'EFB Access', 'EFB Copy', 'EFB to Texture',
            'Emulate Formate Changes', 'Use XFB', 'Use Real XFB', 'Memory Cards', 'Memory Card Blank',
            'Bongos Pluged In', 'Sync GPU', 'Netplay', 'SYSCONF PAL60', 'Reserved2', 'Disc 2 Name',
            'SHA1 git revision', 'DSP IROM Hash', 'DSP COEF Hash', 'Tick Count', 'Reserved3')
    values = struct.unpack('<6s?B?4QL32s16s16s16sQ6?B7?3B3?12s40s20s2LQ11s', data[0x4:0x100])
    header.update(dict(zip(keys, values)))
    return header

def _process_input(data):
    new = bytearray(8)
    old_byte1 = data[0]
    old_byte2 = data[1]
    new_byte1 = 0
    new_byte2 = 0

    new[2] = data[4]
    new[3] = data[5]
    new[4] = data[6]
    new[5] = data[7]
    new[6] = data[2]
    new[7] = data[3]

    new_byte1 += (old_byte1 & 0x01) << 4 # start
    new_byte1 += (old_byte1 & 0x10) >> 1 # Y
    new_byte1 += (old_byte1 & 0x08) >> 1 # X
    new_byte1 += (old_byte1 & 0x04) >> 1 # B
    new_byte1 += (old_byte1 & 0x02) >> 1 # A

    new_byte2 += (old_byte2 & 0x04) << 4 # L
    new_byte2 += (old_byte2 & 0x08) << 2 # R
    new_byte2 += (old_byte1 & 0x20) >> 1 # Z
    new_byte2 += (old_byte1 & 0x40) >> 3 # DpadU
    new_byte2 += (old_byte1 & 0x80) >> 5 # DpadD
    new_byte2 += (old_byte2 & 0x02)      # DpadR
    new_byte2 += (old_byte2 & 0x01)      # DpadL

    new[0] = new_byte1
    new[1] = new_byte2
    return new

def read_input(data, header=None):
    if header == None:
        header = read_header(data)
    controllerCount = 0
    if header['Controllers'] & 0x1 != 0:
        controllerCount += 1
    if header['Controllers'] & 0x2 != 0:
        controllerCount += 1
    if header['Controllers'] & 0x4 != 0:
        controllerCount += 1
    if header['Controllers'] & 0x8 != 0:
        controllerCount += 1
    if header['Controllers'] & 0xf0 != 0:
        raise RuntimeError('Movie Has Unsupported Controllers')
    start = 0x100
    input_struct = struct.Struct('8s'*controllerCount)
    input_iter = input_struct.iter_unpack(data[start:])
    input_data = []
    #alternate = 0
    for frame in input_iter:
        #alternate = 1 - alternate
        #if alternate == 1:
        #    continue;
        fd = b''
        for pd in frame:
            fd += _process_input(pd)
        input_data.append(fd)
    return input_data

def main():
    try:
        file = sys.argv[1]
    except:
        print(f'Usage {sys.argv[0]} <movie file>')
        sys.exit()
    with open(file, 'rb') as f:
        data = f.read()
    header = read_header(data)
    for k, v in header.items():
        if 'unused' in k:
            continue
        else:
            print('{}: {}'.format(k, v))
    inputs = read_input(data, header)

if __name__ == '__main__':
    main()