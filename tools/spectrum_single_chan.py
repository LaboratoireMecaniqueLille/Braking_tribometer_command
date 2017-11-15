#coding: utf-8
from __future__ import division

import crappy

def apply_gain(data):
  data[label] *= gain
  return data

channel = 9 # Capacitive sensor
vrange = 10000 # -10/+10V (in mV)
gain = 250 # µm/V
label = 'Distance (micron)'

gain *= vrange/32000000


spectrum = crappy.blocks.IOBlock('spectrum',ranges=[vrange],
    channels=[channel],
    streamer=True,
    labels=['t(s)','stream'])

graph = crappy.blocks.Grapher(('t(s)',label))
crappy.link(spectrum,graph,
    condition=[crappy.condition.Demux([label],mean=False),apply_gain])

crappy.start()
