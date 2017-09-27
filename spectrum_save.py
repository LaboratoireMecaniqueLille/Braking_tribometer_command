#coding: utf-8
from __future__ import division, print_function

import crappy
import time

"""
VOIES:
0: Trig venant de la Labjack (V)
1: Effort Normal (N)
2: Effort tangentiel (N)
3: Effort radial (N)
4: Effort du ressort (N)
5: couple (Nm)
6: top-tour (V)
7: Vitesse (t/min)
"""

channels = list(range(8))
ranges = [10000]*len(channels) # -10/+10V (in mV)
freq = 100000
timestamp = time.strftime("%y-%m-%d_%Hh%M")

chan_names = ['ch'+str(i) for i in channels]

spectrum = crappy.blocks.IOBlock('spectrum',ranges=ranges,
    channels=channels,
    streamer=True,
    labels=['t(s)','stream'])


gains = [1,500,500,500,2060,50,1,413]
gains = [g*(r/32000000) for g,r in zip(gains,ranges)]
# Full range: DL=32000 (et /1000 pour passer de mV à V)

#graph = crappy.blocks.Grapher(*[('t(s)',i) for i in chan_names])
hsaver = crappy.blocks.Hdf_saver(timestamp+"/spectrum.h5",
    metadata={'channels':channels,'ranges':ranges,'freq':freq,'gains':gains})
crappy.link(spectrum,hsaver)
"""
crappy.link(spectrum,graph,
    condition=crappy.condition.Demux(chan_names,mean=False))
"""

crappy.start()
