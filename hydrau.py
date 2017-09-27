#coding: utf-8
from __future__ import print_function

from time import time
import Tkinter as tk

from crappy import blocks,link,start,condition

class ButtonInput(blocks.MasterBlock):
  def __init__(self):
    blocks.MasterBlock.__init__(self)
    self.freq = 50
    self.value = 0
    self.labels = ['t(s)','hydrau']

  def prepare(self):
    self.root = tk.Tk()
    self.button = tk.Button(text="Toggle",command=self.toggle)
    self.button.pack()

  def toggle(self):
    self.value = int(not self.value)
    print("Value=",self.value)

  def loop(self):
    self.send([time()-self.t0,self.value])
    self.root.update()

t = .2
tempo = "delay="+str(t)
tempo2 = "delay="+str(2*t)

hydrau_path_fio2 = [
    {'type':'constant','value':1,'condition':'hydrau<1'}, #Sorti, jusqu'à 0
    {'type':'constant','value':1,'condition':tempo}, # Attendre avant de rentrer
    {'type':'constant','value':0,'condition':tempo}, # Rentrer, attendre la fin
    {'type':'constant','value':0,'condition':'hydrau>0'}, # Avant de recommencer
    ]

hydrau_path_fio3 = [
    {'type':'constant','value':0,'condition':'hydrau<1'}, # Ouvert
    {'type':'constant','value':1,'condition':tempo2}, # fermer jusqu'à 2tempo
    {'type':'constant','value':0,'condition':'hydrau>0'}, # refermer
    {'type':'constant','value':1,'condition':tempo}, # fermer jusqu'à tempo
    ]

gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='h2',freq=50)
gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='h3',freq=50,verbose=True)

bi = ButtonInput()
link(bi,gen_fio2,condition=condition.Trig_on_change("hydrau"))
link(bi,gen_fio3,condition=condition.Trig_on_change("hydrau"))

# ==========  Virtual version ============

gh2 = blocks.Grapher(('t(s)','h2'),freq=1)
link(gen_fio2,gh2)
gh3 = blocks.Grapher(('t(s)','h3'),freq=1)
link(gen_fio3,gh3)

#"""
# ========== Physical version =========
lj = blocks.IOBlock("Labjack_t7",identifier="470012972",channels=[
  {'name':'FIO2','direction':True}, # Hydrau
  {'name':'FIO3','direction':True}, # ..
  ],cmd_labels=['h2','h3'])
link(gen_fio2,lj)
link(gen_fio3,lj)
# =====================================
"""
"""
start()
