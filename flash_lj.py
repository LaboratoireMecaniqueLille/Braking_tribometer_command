#coding: utf-8
import re
from time import sleep
from labjack import ljm

FILE = "./pid_lj.lua"

source = open(FILE,"r").read()

#print(source)

# Remove the comments (makes the code lighter)
source = re.sub("\s*--.+","",source)
# Remove the spacing lines
source = re.sub("\n+","\n",source,flags=re.MULTILINE)

print(source)

h = ljm.openS("ANY")

if ljm.eReadName(h,"LUA_RUN"):
  ljm.eWriteName(h,"LUA_RUN",0)
  sleep(1)
ljm.eWriteName(h,"LUA_RUN",0)

ljm.eWriteName(h,"LUA_SOURCE_SIZE",len(source))
ljm.eWriteNameArray(h,"LUA_SOURCE_WRITE",len(source),[ord(i) for i in source])
ljm.eWriteName(h,"LUA_RUN",1)
ljm.close(h)

print("Done")
