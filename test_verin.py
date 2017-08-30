#coding: utf-8

import crappy

lj = crappy.blocks.IOBlock("Labjack_t7",identifier="470012972",channels=[
  {'name':'FIO2','direction':True}, # Hydrau
  {'name':'FIO3','direction':True}, # ..
  ],cmd_labels=['h2','h3'])

t = .2
tempo = "delay="+str(t)
tempo2 = "delay="+str(2*t)

hydrau_path_fio2 = [
    {'type':'constant','value':1,'condition':'hydrau<1'}, #Sorti, jusqu'à 0
    {'type':'constant','value':1,'condition':tempo}, # Attendre avant de rentrer
    {'type':'constant','value':0,'condition':tempo}, # Rentrer, attendre la fin
    {'type':'constant','value':0,'condition':'hydrau>0'}, # Avant de recommencer
    ]

hydrau_path_fio3 = [
    {'type':'constant','value':0,'condition':'hydrau<1'}, # Ouvert
    {'type':'constant','value':1,'condition':tempo2}, # fermer jusqu'à 2tempo
    {'type':'constant','value':0,'condition':'hydrau>0'}, # refermer
    {'type':'constant','value':1,'condition':tempo}, # fermer jusqu'à tempo
    ]

gen_fio2 = crappy.blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='h2')
gen_fio3 = crappy.blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='h3')

gen = crappy.blocks.Generator(
    [{'type':'cyclic',"value1":1,"value2":0,
      "condition1":"delay=10","condition2":"delay=5"}],
    cmd_label='hydrau',repeat=True)

crappy.link(gen,gen_fio2)
crappy.link(gen,gen_fio3)

crappy.link(gen_fio2,lj)
crappy.link(gen_fio3,lj)

crappy.start()
