import string
import csv

z = open("zipcodes.txt")
f = open("bostonzips.py", "w")

f.write("from presurvey.models import BostonZip\n\n")

line = z.readline()
while line:
    if string.find(line, "-") == -1:
        line = string.strip(line)
        line = string.split(line, ", ")
        f.write("b = BostonZip(zipcode='%s', name='%s')\n"%(line[0],line[1]))
        f.write("b.save()\n")
    line = z.readline()

z.close()
f.close()

