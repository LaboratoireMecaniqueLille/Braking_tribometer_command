#coding: utf-8
from __future__ import division

import crappy

channels = [6,8] # Read the Top and the cap sensor
ranges = [10000]*len(channels) # -10/+10V (in mV)
# This will NOT apply the gain to the stream, only save a key in the h5
gains = [1]*len(channels)
save_file = "./disp.h5"

chan_names = ['ch'+str(i) for i in channels]

spectrum = crappy.blocks.IOBlock('spectrum',ranges=ranges,
    channels=channels,
    streamer=True,
    labels=['t(s)','stream'])

graph = crappy.blocks.Grapher(*[('t(s)',i) for i in chan_names])
hsaver = crappy.blocks.Hdf_saver("./out.h5",
    metadata={'channels':channels,'ranges':ranges,'freq':100000,
      'factor':[r*g/32000000 for r,g in zip(ranges,gains)]})
crappy.link(spectrum,hsaver)
crappy.link(spectrum,graph,
    condition=crappy.condition.Demux(chan_names,mean=False))

crappy.start()
