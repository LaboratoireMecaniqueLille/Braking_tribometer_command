#coding: utf-8
from __future__ import print_function

import re
from time import sleep
from labjack import ljm

"""
If called, this file will read the content of ./pid_lj.lua
and write it to the first Labjack found

It can also be used to import flash, a function to write and start the script
"""

def flash(h,source):
  """
  Flash a LUA script on the Labjack

  h: handle of the device
  source: The code to write (str)
  """

  # Remove the comments (makes the code lighter)
  source = re.sub("\s*--.+","",source)
  # Remove the spacing lines
  source = re.sub("\n+","\n",source,flags=re.MULTILINE)
  if ljm.eReadName(h,"LUA_RUN"):
    ljm.eWriteName(h,"LUA_RUN",0)
    sleep(1)
  ljm.eWriteName(h,"LUA_RUN",0)

  ljm.eWriteName(h,"LUA_SOURCE_SIZE",len(source))
  ljm.eWriteNameArray(h,"LUA_SOURCE_WRITE",len(source),[ord(i) for i in source])
  ljm.eWriteName(h,"LUA_RUN",1)

if __name__ == '__main__':
  print("This will write the script on the first Labjack found.")
  print("Make sure it is the only one connected!")
  if raw_input("Continue y/[n] ?").lower() == 'y':
    h = ljm.openS("ANY")
    flash(h,open("./pid_lj.lua","r").read())
    ljm.close(h)
    print("Done!")
  else:
    print("Aborted.")
