import string
import csv

z = open("boston.csv")
f = open("bostonzips2.py", "w")

f.write("from presurvey.models import BostonZip\n\n")


for line in csv.reader(z):
    dist = line[4].split(" ")[0]
    f.write("b = BostonZip(zipcode='%s', name='%s', distance='%s')\n"%(line[0],line[1], dist))
    f.write("b.save()\n")

z.close()
f.close()

