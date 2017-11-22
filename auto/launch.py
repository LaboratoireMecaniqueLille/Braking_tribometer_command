#coding: utf-8
from __future__ import division, print_function

from multiprocessing import Pipe
import serial
from time import sleep
import Tkinter as tk

from crappy import blocks,start,condition,link,stop

from funcs import prepare_path

ports_5018 = ['/dev/ttyS5','/dev/ttyS6','/dev/ttyS7']

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
    self.root.resizable(height=False,width=False)
    self.root.geometry('{}x{}'.format(420, 100))
    tk.Button(self.root,text="Stop",command=self.term).pack()
    self.label = tk.Label(self.root,text="Initializing...",wraplength=400)
    self.label.pack()
    self.label_next = tk.Label(self.root,text="Initializing...",wraplength=400)
    self.label_next.pack()

  def loop(self):
    if self.inputs[0].poll():
      i = self.inputs[0].recv()['step']
      print(self.d[i])
      self.label.configure(text=self.d[i]+" (%d/%d)"%(i+1,len(self.d)))
      self.label_next.configure(
          text="next step: "+self.d[min(i+1,len(self.d)-1)])
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

class Bypass_trig():
  """
  This condition is used to bypass the generator in case of cancelation
  """
  def __init__(self,pipe,value):
    self.p = pipe
    self.v = value
    self.last = None

  def evaluate(self,d):
    if not self.p.poll():
      if d['step'] != self.last:
        self.last = d['step']
        return d
    else:
      return self.v

# ==        This function is the core of the program:        ==
# == It interprets the settings to actually perform the test ==
def launch(path,spectrum,lj2,graph,savepath,enable_drawing):
  print("Let's go!",path,spectrum,lj2,graph)

  # To know if step_gen has additional inputs
  l_in = [d['value'] for d in path if d['type'] == 'wait_cd']
  l_in = [v.split('<')[0] if '<' in v else v.split('>')[0] for v in l_in]

  paths = prepare_path(path)

  bp_p1,bp_p2 = Pipe() # To update the Bypass conditions
  # == The master generator: it orchestrates the whole test ==
  step_gen = blocks.Generator(paths['state'],cmd_label="step",
      spam=True,freq=20)

  # == The little windows to abort the test and print its status ==
  popup = Popup(paths['status'],bp_p1)
  link(step_gen,popup,condition=condition.Trig_on_change("step"))

  # == Motor speed ==
  speed_gen = blocks.Generator(paths['speed'],
      cmd_label="lj1_speed_cmd",freq=300)
  link(step_gen,speed_gen,
      condition=Bypass_trig(bp_p2,{'step':len(paths['state'])-1}))

  # == Pad force (when fmode=1), target torque (when fmode=2) ==
  force_gen = blocks.Generator(paths['force'],cmd_label="lj1_fcmd")
  link(step_gen,force_gen,
      condition=Bypass_trig(bp_p2,{'step':len(paths['state'])-1}))

  # == How do we control the pad (0:Pos, 1:Force, 2:Torque)
  fmode_gen = blocks.Generator(paths['fmode'],cmd_label="lj1_fmode")
  link(step_gen,fmode_gen,
      condition=Bypass_trig(bp_p2,{'step':len(paths['state'])-1}))

  # == Pad pos (and enable/disable analog control) ==
  padpos_gen = blocks.Generator(paths['pad'],cmd_label="pad")
  link(step_gen,padpos_gen,
      condition=Bypass_trig(bp_p2,{'step':len(paths['state'])-1}))

  # == These generators command each valve of the hydraulic actuator ==
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

  # They simply take 1 to push the actuator out and 0 to retract it
  gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='lj1_h2')
  gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='lj1_h3')
  # Now we just need a "parent" generator that simply sends 0 and 1
  gen_hydrau = blocks.Generator(paths['hydrau'],cmd_label="hydrau",cmd=1)
  link(gen_hydrau,gen_fio2,condition=Bypass(bp_p2,{'hydrau':1}))
  link(gen_hydrau,gen_fio3,condition=Bypass(bp_p2,{'hydrau':1}))
  link(step_gen,gen_hydrau,
      condition=Bypass(bp_p2,{'step':len(paths['state'])-1}))

  # == To drive the pad position and en/disable the analog input ==
  gen_pad = blocks.Generator(paths['pad'],cmd_label="pad")
  link(step_gen,gen_pad,condition=Bypass(bp_p2,{'step':len(paths['state'])-1}))

  servostar = blocks.Machine([{"type":"Servostar","cmd":"pad",
    "mode":"position", "device":"/dev/ttyS4"}])
  link(padpos_gen,servostar)

  # == Creating the pulse generator to trig the camera ==
  gen_trig = blocks.Generator(
      [dict(type='constant',value=0,condition='delay=1'),
      dict(type='constant',value=5,condition='delay=1'),
      dict(type='constant',value=0,condition=None),
      ],cmd_label='lj1_trig',freq=2)

  # == Creating the first Labjack, config is read from lj1_chan.py ==
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
  link(gen_trig,labjack1)

  link(labjack1,speed_gen)
  link(labjack1,step_gen)

  # And the saver
  lj1_saver = blocks.Saver(savepath+"lj1.csv")
  link(labjack1,lj1_saver)


  # == Creating the Spectrum block ==
  spec_chan = []
  spec_labels = {}
  spec_ranges = {}
  spec_gains = {}

  spectrum_freq,spectrum = spectrum
  for c in spectrum:
    spec_chan.append(c['chan'])
    spec_labels[c['chan']] = c['lbl']
    c['range'] = int(1000*c['range']) # V to mV
    spec_ranges[c['chan']] = c['range']\
        if c['range'] in [50,250,500,1000,2000,5000,10000] else 10000
    spec_gains[c['chan']] = c['gain']
  if spectrum: # If the spectrum is not used, don't create the blocks
    from spectrum_tools import HFSplit,check_chan
    # check_chan will make sure that the user opens the correct chans (see doc)
    spec_chan = check_chan(spec_chan)

    for c in spec_chan:
      if c not in spec_labels:
        spec_labels[c] = "UNUSED%d"%c
        spec_ranges[c] = 10000
        spec_gains[c] = 1

    spectrum_block = blocks.IOBlock("spectrum",channels=spec_chan,
        ranges=spec_ranges,
        samplerate=int(1000*spectrum_freq),
        streamer=True)
    # And the saver
    # Simply multiply the chan values by its factor to get the physical value
    spectrum_save = blocks.Hdf_saver(savepath+"spectrum.h5",
        metadata={'channels':spec_chan,
                  'names':[spec_labels[k] for k in spec_chan],
                  'ranges':[spec_ranges[k] for k in spec_chan],
                  'gains':[spec_gains[k] for k in spec_chan],
                  'factor':[r*g/32000000 for r,g in zip([spec_ranges[k] for k in spec_chan],
                    [spec_gains[k] for k in spec_chan])],
                  'freq':int(1000*spectrum_freq),
          })
    link(spectrum_block,spectrum_save)

  # == Creating the second Labjack ==
  freq_lj2,lj2 = lj2
  if lj2:
    lj2_labels = ['t(s)']
    for c in lj2:
      lj2_labels.append(c['lbl'])
      del c['lbl']
    labjack2 = blocks.IOBlock("Labjack_t7",identifier="470014418",
        channels=lj2,labels=lj2_labels,freq=freq_lj2,verbose=True)

    # And the saver
    lj2_saver = blocks.Saver(savepath+"lj2.csv")
    link(labjack2,lj2_saver)

  # == Linking additional inputs to step_gen (if necessary) ==
  if any([lbl in l_in for lbl in lj2_labels]):
    link(labjack2,step_gen)
  if any([lbl in l_in for lbl in [c['lbl'] for c in spectrum]]):
    link(spectrum_block,step_gen,
        condition=HFSplit(spec_labels,spec_chan,spec_gains,spec_ranges))

  # == Creating the graphs ==
  graphs = []
  for g in graph.values():
    graphs.append(blocks.Grapher(*[('t(s)',lbl) for lbl in g],backend='qt4agg'))
    # Link to the concerned blocks
    if any([lbl in [c['lbl'] for c in spectrum] for lbl in g]):
      # Note that the performance of HFSplit is uncertain, try to avoid !
      link(spectrum_block,graphs[-1],
        condition=HFSplit(spec_labels,spec_chan,spec_gains,spec_ranges))
    if any([lbl in lj2_labels for lbl in g]):
      link(labjack2,graphs[-1])
    if any([lbl in in_chan.keys() for lbl in g]):
      link(labjack1,graphs[-1])

  # == Creating the Drawing block (if asked to) ==
  if enable_drawing:
    from pad_config import get_drawing
    draw_block = get_drawing(lj2_labels)
    link(labjack2,draw_block)

  # == Last thing: reset the 5018 conditionners ==
  for port in ports_5018:
    s = serial.Serial(port,baudrate=115200)
    s.write('9,0\r\n')
    sleep(.1)
    s.write('9,1\r\n')
    sleep(.1)
    s.close()

  # == ... and GO ! ==
  start()
