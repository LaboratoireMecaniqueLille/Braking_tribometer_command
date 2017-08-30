#coding: utf-8

import crappy

servostar = crappy.actuator.Servostar('/dev/ttyS4')
servostar.open()

servostar.set_mode_analog()

lj = crappy.blocks.IOBlock("Labjack_t7",channels=[
  {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
  {'name':46000,'direction':True},
  {'name':46002,'direction':True},
  ],labels=['t(s)','F(N)'],cmd_labels=['cmd','pid'])

gen_pad = crappy.blocks.Generator([{'type':'sine','freq':.2,'amplitude':500,
'offset':350,'condition':'delay=600'}])

gen_pid = crappy.blocks.Generator([{'type':'cyclic','value1':0,'value2':1,
                  'condition1':'delay=3','condition2':'delay=1'}],
                  repeat=True,cmd_label='pid')
crappy.link(gen_pid,lj)
crappy.link(gen_pad,lj)

g = crappy.blocks.Grapher(('t(s)','cmd'),('t(s)','F(N)'))

crappy.link(lj,g)
crappy.link(gen_pad,g)

crappy.start()
