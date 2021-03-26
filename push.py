import sys
import os

name = ' '.join(sys.argv[1:])

os.system("git add .")
os.system("git commit -m " + '"' + name + '"')
os.system("git push origin main")