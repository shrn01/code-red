#! python

import sys
import os

name = ' '.join(sys.argv[1:])

command = "git add ."
print("executing",command)
os.system(command)

command = "git commit -m " + '"' + name + '"'
print("executing",command)
os.system(command)

command = "git push origin main"
print("executing",command)
os.system(command)