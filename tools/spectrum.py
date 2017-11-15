#coding: utf-8
from __future__ import division

import crappy

def apply_gain(data):
  for k,g in zip(chan_names,gains):
    data[k] *= g
  return data

channels = list(range(16)) # Every channel (from 0 to 15)
ranges = [10000]*len(channels) # -10/+10V (in mV)
# This will NOT apply the gain to the stream, only save a key in the h5
gains = [1]*len(channels)

for i in range(len(gains)):
  gains[i] *= ranges[i]/32000000

chan_names = ['ch'+str(i) for i in channels]

spectrum = crappy.blocks.IOBlock('spectrum',ranges=ranges,
    channels=channels,
    streamer=True,
    labels=['t(s)','stream'])

graph = crappy.blocks.Grapher(*[('t(s)',i) for i in chan_names])
crappy.link(spectrum,graph,
    condition=[crappy.condition.Demux(chan_names,mean=False),apply_gain])

crappy.start()
