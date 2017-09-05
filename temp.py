#coding: utf-8

import crappy

comedi = crappy.blocks.IOBlock('comedi',
    channels=range(14),
    gain=[10]+[1350]*13,
    labels=['t(s)','trig']+['T'+str(i) for i in range(1,12)]+['Tdisc1','Tdisc2'],
    make_zero=False,
    )

graph = crappy.blocks.Grapher(*[('t(s)','T'+str(i)) for i in range(1,7)+range(8,11)])

coord = [ # Coordinates for the thermocouples
(185, 430),  # T1
(145, 320),  # T2
(105, 220),  # T3
(720, 370),  # T4
(720, 250),  # T5
(720, 125),  # T6
(1220, 410),  # T7
(1260, 320),  # T8
(1300, 230),  # T9
]

coord_disc = [
(100,800), #Tdisc1
(100,920) # Tdisc2
]

options = [{'type':'dot_text',
            'coord':coord[i],
            'text':'T{} = %.1f'.format(i+1),
            'label':'T'+str(i+1)} for i in range(9)]\
          +[{'type':'text',
            'coord':coord_disc[i],
            'text':'Tdisc{} = %.1f'.format(i+1),
            'label':'T'+str(i+10)} for i in range(2)]


draw = crappy.blocks.Drawing("/home/tribo/Code/crappy/data/Pad.png",
                             options,
                             crange=[20,300],
                             title="Temperatures")




crappy.link(comedi,graph)
crappy.link(comedi,draw)
crappy.start()
