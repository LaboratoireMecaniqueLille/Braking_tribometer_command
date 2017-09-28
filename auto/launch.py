#coding: utf-8
from __future__ import division, print_function

from multiprocessing import Pipe

from crappy import blocks,start,condition,link,stop
from time import ctime,sleep

import Tkinter as tk

class Popup(blocks.MasterBlock):
  """
  The window that will allow to stop the test and give the current step
  """
  def __init__(self,d,pipe):
    blocks.MasterBlock.__init__(self)
    self.d = d
    self.freq = 2
    self.pipe = pipe

  def prepare(self):
    self.root = tk.Tk()
    tk.Button(self.root,text="Stop",command=self.term).pack()
    self.label = tk.Label(self.root,text="Initializing...")
    self.label.pack()

  def loop(self):
    if self.inputs[0].poll():
      i = self.inputs[0].recv()['step']
      print(self.d[i])
      self.label.configure(text=self.d[i]+" (%d/%d)"%(i+1,len(self.d)))
    self.root.update()

  def term(self):
    self.pipe.send(1)
    sleep(1)
    stop()

  def finish(self):
    self.root.destroy()

class Bypass():
  """
  This condition is used to bypass the generator in case of cancelation
  """
  def __init__(self,pipe,value):
    self.p = pipe
    self.v = value

  def evaluate(self,d):
    if not self.p.poll():
      return d
    return self.v

def launch(path,spectrum,lj2,graph,savepath,enable_drawing):
  print("Let's go!",path,spectrum,lj2,graph)
  if savepath[-1] != "/":
    savepath += "/"
  savepath += ctime()[:-5].replace(" ","_")+"/"

  # This is used to know if step_gen has additional inputs
  l_in = [d['value'] for d in path if d['type'] == 'wait_cd']
  l_in = [v.split('<')[0] if '<' in v else v.split('>')[0] for v in l_in]

  from funcs import prepare_path
  paths = prepare_path(path)

  bp_p1,bp_p2 = Pipe()
  step_gen = blocks.Generator(paths['state'],cmd_label="step",spam=True,freq=20)
  popup = Popup(paths['status'],bp_p1)
  link(step_gen,popup,condition=condition.Trig_on_change("step"))


  speed_gen = blocks.Generator(paths['speed'],cmd_label="lj1_speed_cmd",freq=300)
  link(step_gen,speed_gen,condition=condition.Trig_on_change('step'))

  force_gen = blocks.Generator(paths['force'],cmd_label="lj1_fcmd")
  link(step_gen,force_gen,condition=condition.Trig_on_change('step'))

  fmode_gen = blocks.Generator(paths['fmode'],cmd_label="lj1_fmode")
  link(step_gen,fmode_gen,condition=condition.Trig_on_change('step'))

  padpos_gen = blocks.Generator(paths['pad'],cmd_label="pad")
  link(step_gen,padpos_gen,condition=condition.Trig_on_change('step'))

  t = .2
  tempo = "delay="+str(t)
  tempo2 = "delay="+str(2*t)
  hydrau_path_fio2 = [
      {'type':'constant','value':0,'condition':'hydrau>0'}, # Consider it out
      {'type':'constant','value':1,'condition':'hydrau<1'}, # Asking to retract
      {'type':'constant','value':1,'condition':tempo}, # Wait...
      {'type':'constant','value':0,'condition':tempo}, # Retract and wait
      ]

  hydrau_path_fio3 = [
      {'type':'constant','value':0,'condition':'hydrau>0'}, # We asked it out
      {'type':'constant','value':1,'condition':tempo}, # Load...
      {'type':'constant','value':0,'condition':'hydrau<1'}, # Now go
      {'type':'constant','value':1,'condition':tempo2}, # Load again, to go in
      ]

  gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='lj1_h2')
  gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='lj1_h3')

  gen_hydrau = blocks.Generator(paths['hydrau'],cmd_label="hydrau",cmd=1)
  link(gen_hydrau,gen_fio2,condition=Bypass(bp_p2,{'hydrau':1}))
  link(gen_hydrau,gen_fio3,condition=Bypass(bp_p2,{'hydrau':1}))
  link(step_gen,gen_hydrau,condition=Bypass(bp_p2,{'step':len(paths['state'])-1}))

  gen_pad = blocks.Generator(paths['pad'],cmd_label="pad")
  link(step_gen,gen_pad,condition=Bypass(bp_p2,{'step':len(paths['state'])-1}))

  servostar = blocks.Machine([{"type":"Servostar","cmd":"pad","mode":"position",
                              "device":"/dev/ttyS4"}])
  link(padpos_gen,servostar)

  # Creating the first Labjack, config is read from lj1_chan.py
  from lj1_chan import in_chan,out_chan,identifier
  lj1_chan = []
  lj1_labels = ['t(s)']
  lj1_out_labels = []
  for k,v in in_chan.iteritems():
    lj1_chan.append(v)
    lj1_labels.append(k)
  for k,v in out_chan.iteritems():
    lj1_chan.append(v)
    lj1_out_labels.append(k)
  labjack1 = blocks.IOBlock("Labjack_t7",identifier=identifier,
      channels=lj1_chan, labels=lj1_labels,cmd_labels=lj1_out_labels)

  link(speed_gen,labjack1,condition=Bypass(bp_p2,{'lj1_speed_cmd':0}))
  link(gen_fio2,labjack1)
  link(gen_fio3,labjack1)
  link(force_gen,labjack1,condition=Bypass(bp_p2,{'lj1_fcmd':0}))
  link(fmode_gen,labjack1,condition=Bypass(bp_p2,{'lj1_fmode':0}))

  link(labjack1,speed_gen)
  link(labjack1,step_gen)

  # == And the associated saver
  lj1_saver = blocks.Saver(savepath+"lj1.csv")
  link(labjack1,lj1_saver)


  # Creating the Spectrum block
  spec_chan = []
  spec_labels = []
  spec_ranges = []
  spec_gains = {}

  spectrum_freq,spectrum = spectrum
  for c in spectrum:
    spec_chan.append(c['chan'])
    spec_labels.append(c['lbl'])
    c['range'] = int(1000*c['range']) # V to mV
    spec_ranges.append(c['range']\
        if c['range'] in [50,250,500,1000,2000,5000,10000] else 10000)
    spec_gains[c['chan']] = c['gain']
  if spectrum:
    from spectrum_tools import HFSplit,check_chan
    spec_chan,spec_labels,spec_ranges,spec_gains = \
        check_chan(spec_chan,spec_labels,spec_ranges,spec_gains)

    spectrum_block = blocks.IOBlock("spectrum",channels=spec_chan,
        ranges=spec_ranges,
        samplerate=int(1000*spectrum_freq),
        streamer=True)

    spectrum_save = blocks.Hdf_saver(savepath+"spectrum.h5",
        metadata={'channels':spec_chan,
                  'names':spec_labels,
                  'ranges':spec_ranges,
                  'gains':[spec_gains[k] for k in sorted(spec_gains.keys())],
                  'freq':int(1000*spectrum_freq),
          })
    link(spectrum_block,spectrum_save)

  # Creating the second Labjack
  freq_lj2 = lj2[0]
  lj2 = lj2[1]
  if lj2:
    print("LJ2=",lj2)
    lj2_labels = ['t(s)']
    for c in lj2:
      lj2_labels.append(c['lbl'])
      del c['lbl']
    labjack2 = blocks.IOBlock("Labjack_t7",identifier="470014418",
        channels=lj2,labels=lj2_labels,freq=freq_lj2,verbose=True)

    # == And the saver
    lj2_saver = blocks.Saver(savepath+"lj2.csv")
    link(labjack2,lj2_saver)

  # Linking additional inputs to step_gen
  if any([lbl in l_in for lbl in lj2_labels]):
    link(labjack2,step_gen)
  if any([lbl in l_in for lbl in [c['lbl'] for c in spectrum]]):
    link(spectrum_block,step_gen,
        condition=HFSplit(spec_labels,spec_chan,spec_gains,spec_ranges))

  # Creating the graphs
  graphs = []
  for g in graph.values():
    #print("Graph:",g)
    graphs.append(blocks.Grapher(*[('t(s)',lbl) for lbl in g],backend='qt4agg'))
    # Link to the concerned blocks
    if any([lbl in [c['lbl'] for c in spectrum] for lbl in g]):
      link(spectrum_block,graphs[-1],
        condition=HFSplit(spec_labels,spec_chan,spec_gains,spec_ranges))
    if any([lbl in lj2_labels for lbl in g]):
      link(labjack2,graphs[-1])
    if any([lbl in in_chan.keys() for lbl in g]):
      link(labjack1,graphs[-1])

  if enable_drawing:
    from pad_config import get_drawing
    draw_block = get_drawing(lj2_labels)
    link(labjack2,draw_block)

  start()
