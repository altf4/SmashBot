#!python
import os
from PIL import Image
import argparse
import csv
#sudo pip install Pillow

parser = argparse.ArgumentParser(description='Batch convert Melee attack animation GIFs into frame data CSVs.')
parser.add_argument('--input', help='Folder containing hitbox GIFs')
parser.add_argument('--output', help='Output CSV file')

args = parser.parse_args()

args.input

#Open output file for writing
with open(args.output, 'w') as csvfile:
    fieldnames = ['Character', 'Animation', 'hasGrab', 'hasAttack', 'leftEdge', 'rightEdge', 'bottomEdge', 'topEdge']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    #Loop over every GIF file in the given directory
    for filename in os.listdir(args.input):
        if not (filename.endswith('gif')):
            continue

        gif = Image.open(args.input + "/" + filename)
        width, height = gif.size
        print filename, width, height

        #Loop over every frame in the GIF
        try:
            i = 0
            while True:
                gif.seek(i)
                frame_index = gif.tell()
                i = i+1
                frame = gif.convert("RGB")
                pixels = list(frame.getdata())
                red_count = 0
                bottom = height
                top = 0
                left = width
                right = 0
                row = dict()
                row['Character'] = 'Marth' #TODO
                row['hasGrab'] = False
                row['Animation'] = os.path.splitext(os.path.basename(filename))[0]

                #Loop through each pixel of the frame
                for x in range(width):
                    for y in range(height):
                        pixel = pixels[x + (y*width)]
                        #Hitbox red tends to be ~130,0,0. But let's have a little wiggle room
                        if (pixel[0] > 110) and (pixel[1] < 10) and (pixel[2] < 10):
                            red_count = red_count+1
                            #print x,y
                            #update any boundaries that might have changed
                            if x < left:
                                left = x
                            if x > right:
                                right = x
                            if y < bottom:
                                bottom = y
                            if y > top:
                                top = y

                if red_count > 1000:
                    print "Frame: " + str(frame_index+1) + " has a hitbox"
                    print "Bounds: ", left, right, top, bottom
                    row['hasAttack'] = True
                else:
                    bottom = 0
                    top = 0
                    left = 0
                    right = 0
                    row['hasAttack'] = False

                row['topEdge'] = top
                row['bottomEdge'] = bottom
                row['leftEdge'] = left
                row['rightEdge'] = right
                writer.writerow(row)


        except EOFError as e:
            pass
