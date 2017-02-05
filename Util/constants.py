#!/usr/bin/env python

import csv


def write_line(f, string=""):
    f.write(string)
    f.write("\n")

with open('Util/Constants.h', 'w+') as f:
    write_line(f, "#ifndef CONSTANTS_H")
    write_line(f, "#define CONSTANTS_H")
    write_line(f)
    with open('Util/constants.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            variable_name = row[0]
            value = row[1]
            try:
                comment = row[2]
                write_line(f, "//" + comment)
            except IndexError:
                pass
            write_line(f, "#define {} {}".format(variable_name, value))
            write_line(f)
    f.write("#endif // CONSTANTS_H")

