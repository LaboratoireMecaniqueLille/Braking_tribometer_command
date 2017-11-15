#coding:utf-8

# Script to display the temperatures when a test is not running
import crappy

img = "/home/tribo/Code/crappy/data/Pad.png"

labels = ['t(s)']+['T%d'%(i+1) for i in range(13)]
chan = [{'name':'AIN%d'%(i+1), 'gain':135} for i in range(13)]

lj = crappy.blocks.IOBlock("Labjack_t7",identifier="470014418",
    channels = chan, labels = labels, freq = 20)

points = [
    ("T1", (185,430)),
    ("T2",(145, 320)),
    ("T3",(105, 220)),
    ("T4",(720, 370)),
    ("T5",(720, 250)),
    ("T6",(720, 125)),
    ("T7",(1220, 410)),
    ("T8",(1260, 320)),
    ("T9",(1300, 230)),
]

coord_disc = [
    ('T12',(100,800)),
    ('T13',(100,920)),
]

trange = [20,300] # Temperature scale

options = [{'type':'dot_text',
            'coord':pos,
            'text':l+' = %.1f',
            'label':l} for l,pos in points]

options += [{'type':'text',
            'coord':pos,
            'text':l+' = %.1f',
            'label':l} for l,pos in coord_disc]

draw = crappy.blocks.Drawing(img,options, crange=[20,300],
      title="Temperatures",backend="qt4agg")

crappy.link(lj,draw)
crappy.start()
