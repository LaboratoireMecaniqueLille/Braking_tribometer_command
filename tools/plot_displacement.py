#coding: utf-8
from __future__ import division,print_function

import tables
import matplotlib.pyplot as plt
import numpy as np

import sys

GAIN = 250/3200 # µm/dl
AVG = 0 #10
AUTO_TOP = True
NTOP = 1 # How many tops per revolution
top_chan = 0
cap_chan = 1

def moving_average(a) :
    ret = np.cumsum(a, dtype=float)
    ret[AVG:] = ret[AVG:] - ret[:-AVG]
    return ret[AVG - 1:] / AVG

def detect_tops(data,thresh=15000):
  v = 0
  tops = []
  while len(tops) <= NTOP:
    while data[v] < thresh:
      v +=1
    tops.append(v)
    while data[v] > thresh:
      v += 10
  return tops[0],tops[-1]

if len(sys.argv) > 1:
  f_name = sys.argv[-1]
else:
  f_name = raw_input("file name?")

h = tables.open_file(f_name)
a = h.root.table.read()

if AUTO_TOP:
  x0,x1 = detect_tops(a[:,top_chan])
  print("Detected tops:",x0,x1)
else:
  plt.plot(a[:,top_chan])
  plt.show()
  x0 = int(raw_input("First top ?"))
  x1 = int(raw_input("Second top ?"))

g = 360/(x1-x0)

x = g*(np.arange(a.shape[0])-x0)
y = GAIN*a[:,cap_chan]
if AVG:
  y = moving_average(y)
  x = x[AVG//2-1:-AVG//2]
  print(len(y),len(x))

y -= min(y)
plt.plot(x,y)
plt.show()
