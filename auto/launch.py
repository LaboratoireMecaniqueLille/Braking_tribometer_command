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
  This condition is used to bypass the status in case of cancelation
  """
  def __init__(self,pipe,value):
    self.p = pipe
    self.v = value
    self.last = None

  def evaluate(self,d):
    if not self.p.poll():
      if d['step'] != self.last:
        self.last = d
        return d
    else:
      return self.v

def launch(path,spectrum,lj2,graph,savepath):
  print("Let's go!",path,spectrum,lj2,graph)
  if savepath[-1] != "/":
    savepath += "/"
  savepath += ctime()[:-5].replace(" ","_")+"/"

  # === Preparing path ====

  # Adding a proper ending
  path.append({'type':'end'})

  # Anticipating, to preload the spring before releasing the spring
  for d,n in zip(path[:-1],path[1:]):
    if d['type'] in ['goto','wait']:
      if "force" in n:
        d['force'] = n['force']
      elif "pos" in n:
        d['pos'] = n['pos']
      elif 'torque' in n:
        d['force'] = 20*n['torque'] # Rule of thumbs to preload the spring

  # ==== The functions that will turn each path into the path for the actuators
  def make_goto(speed,delay,force=0,pos=0):
    i = len(state)
    # Acceleration
    if last_step["speed"] < speed:
      state.append({'condition':'lj1_rpm(t/min)>'+str(.99*speed),'value':i})
    else:
      state.append({'condition':'lj1_rpm(t/min)<'+str(1.01*speed),'value':i})
    status_printer.append("Accelerating")
    i += 1
    # Stabilisation
    state.append({'condition':'delay='+str(delay),'value':i})
    status_printer.append("Stabilisating speed")
    # Common path (for acceleration and stabilisation)
    speed_list.append({'type':'constant','value':speed,
                  'condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':force,
                  'condition':'step>'+str(i)})
    force_mode_list.append({'type':'constant','value':int(bool(force)),
                        'condition':'step>'+str(i)})
    if force != 0:
      pad_pos_list.append({'type':'constant','value':False,
                      'condition':'step>'+str(i)})
    else:
      pad_pos_list.append(
          {'type':'constant','value':pos,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':1,'condition':'step>'+str(i)})

  def make_wait(delay,force=0,pos=0):
    i = len(state)
    state.append({'condition':'delay='+str(delay),'value':i})
    status_printer.append("Waiting...")
    speed_list.append({'type':'constant', 'condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':force,
                  'condition':'step>'+str(i)})
    force_mode_list.append({'type':'constant','value':int(bool(force)),
                        'condition':'step>'+str(i)})
    if force != 0:
      pad_pos_list.append({'type':'constant','value':False,
                      'condition':'step>'+str(i)})
    else:
      pad_pos_list.append(
          {'type':'constant','value':pos,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':1,'condition':'step>'+str(i)})

  def make_slow(force,inertia,speed):
    # Next step when we reach the lowest point
    i = len(state)
    state.append({'condition':'lj1_rpm(t/min)<'+str(speed),'value':i})
    status_printer.append(
      "Breaking down to speed {} with inertia simulation".format(
      speed))
    speed_list.append({'type':'inertia','flabel':'lj1_C(Nm)','inertia':inertia,
                  'condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':force,
                  'condition':'step>'+str(i)})
    force_mode_list.append(
        {'type':'constant','value':1,'condition':'step>'+str(i)})
    pad_pos_list.append(
        {'type':'constant','value':False,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':0,'condition':'step>'+str(i)})

  def make_slowp(pos,inertia,speed):
    # Next step when we reach the lowest point
    i = len(state)
    state.append({'condition':'lj1_rpm(t/min)<'+str(speed),'value':i})
    status_printer.append(
      "Breaking down to speed {} with inertia simulation".format(
      speed))
    speed_list.append({'type':'inertia','flabel':'lj1_C(Nm)','inertia':inertia,
                  'condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':0,
                  'condition':'step>'+str(i)})
    force_mode_list.append(
        {'type':'constant','value':1,'condition':'step>'+str(i)})
    pad_pos_list.append(
        {'type':'constant','value':pos,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':0,'condition':'step>'+str(i)})

  def make_cstf(force,delay):
    i = len(state)
    state.append({'condition':'delay='+str(delay),'value':i})
    status_printer.append("Breaking with constant force")
    speed_list.append({'type':'constant','condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':force,
                  'condition':'step>'+str(i)})
    force_mode_list.append(
        {'type':'constant','value':1,'condition':'step>'+str(i)})
    pad_pos_list.append(
        {'type':'constant','value':False,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':0,'condition':'step>'+str(i)})

  def make_cstc(torque,delay):
    i = len(state)
    state.append({'condition':'delay='+str(delay),'value':i})
    status_printer.append("Breaking with constant torque")
    speed_list.append({'type':'constant','condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':torque,
                  'condition':'step>'+str(i)})
    force_mode_list.append(
        {'type':'constant','value':2,'condition':'step>'+str(i)})
    pad_pos_list.append(
        {'type':'constant','value':False,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':0,'condition':'step>'+str(i)})

  def make_cstp(pos,delay):
    i = len(state)
    state.append({'condition':'delay='+str(delay),'value':i})
    status_printer.append("Breaking with constant position")
    speed_list.append({'type':'constant','condition':'step>'+str(i)})
    force_list.append({'type':'constant','value':0,
                  'condition':'step>'+str(i)})
    force_mode_list.append(
        {'type':'constant','value':0,'condition':'step>'+str(i)})
    pad_pos_list.append(
        {'type':'constant','value':pos,'condition':'step>'+str(i)})
    hydrau_list.append({'type':'constant','value':0,'condition':'step>'+str(i)})

  def make_end():
    delay = 'delay=1'
    state.append({'condition':delay,'value':len(state)})
    status_printer.append("End")
    speed_list.append({'type':'constant','value':0,'condition':delay})
    force_list.append({'type':'constant','value':0,'condition':delay})
    force_mode_list.append({'type':'constant','value':0,'condition':delay})
    pad_pos_list.append({'type':'constant','value':0,'condition':delay})
    hydrau_list.append({'type':'constant','value':1,'condition':delay})

  avail = {'goto':make_goto,
           'wait':make_wait,
           'slow':make_slow,
           'slow_p':make_slowp,
           'cst_F':make_cstf,
           'cst_C':make_cstc,
           'cst_P':make_cstp,
           'end':make_end}


  state = [] # Path for the state generator (increment after each substep)
  speed_list = [] # Path for the motor
  force_list = [] # Path for the pad analog input
  force_mode_list = [] # Path for switching on and off the PID
  pad_pos_list = [] # To control the pad mode and set the position
  hydrau_list = [] # To drive the hydraulic actuator


  status_printer = [] # List of each substep to print the current step

  # === Calling these functions according to the user input ====
  last_step = {"speed":0}
  for step in path:
    t = step.pop("type")
    if t in avail:
      avail[t](**step)
    else:
      print("Unknown path:",t)
    last_step.update(step)

  # The state generator only uses constants
  for d in state:
    d['type'] = 'constant'


  # ==== Facultative: display path for debug =====
  #"""
  def display_state():
    for d,s in zip(state,status_printer):
      print(" ",s)
      print("  ",d)

  def display(l):
    for d in l:
      print(" ",d)

  print("State:")
  display_state()
  print("Speed:")
  display(speed_list)
  print("Force:")
  display(force_list)
  print("Force mode:")
  display(force_mode_list)
  print("Pad pos:")
  display(pad_pos_list)
  print("Hydrau:")
  display(hydrau_list)
  #"""

  bp_p1,bp_p2 = Pipe()
  step_gen = blocks.Generator(state,cmd_label="step",spam=True,freq=20)
  popup = Popup(status_printer,bp_p1)
  link(step_gen,popup,condition=condition.Trig_on_change("step"))


  speed_gen = blocks.Generator(speed_list,cmd_label="lj1_speed_cmd",freq=300)
  link(step_gen,speed_gen,condition=Bypass(bp_p2,{'step':len(state)-1}))

  force_gen = blocks.Generator(force_list,cmd_label="lj1_fcmd")
  link(step_gen,force_gen,condition=Bypass(bp_p2,{'step':len(state)-1}))

  fmode_gen = blocks.Generator(force_mode_list,cmd_label="lj1_fmode")
  link(step_gen,fmode_gen,condition=Bypass(bp_p2,{'step':len(state)-1}))

  padpos_gen = blocks.Generator(pad_pos_list,cmd_label="pad")
  link(step_gen,padpos_gen,condition=Bypass(bp_p2,{'step':len(state)-1}))

  t = .2
  tempo = "delay="+str(t)
  tempo2 = "delay="+str(2*t)
  hydrau_path_fio2 = [
      {'type':'constant','value':1,'condition':'hydrau<1'}, #Sorti, jusqu'à 0
      {'type':'constant','value':1,'condition':tempo}, #Attendre avant de rentrer
      {'type':'constant','value':0,'condition':tempo}, #Rentrer, attendre la fin
      {'type':'constant','value':0,'condition':'hydrau>0'}, #Avant de recommencer
      ]

  hydrau_path_fio3 = [
      {'type':'constant','value':0,'condition':'hydrau<1'}, # Ouvert
      {'type':'constant','value':1,'condition':tempo2}, # fermer jusqu'à 2tempo
      {'type':'constant','value':0,'condition':'hydrau>0'}, # refermer
      {'type':'constant','value':1,'condition':tempo}, # fermer jusqu'à tempo
      ]

  gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='lj1_h2')
  gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='lj1_h3')

  gen_hydrau = blocks.Generator(hydrau_list,cmd_label="hydrau",cmd=1)
  link(gen_hydrau,gen_fio2)
  link(gen_hydrau,gen_fio3)
  link(step_gen,gen_hydrau,condition=Bypass(bp_p2,{'step':len(state)-1}))

  gen_pad = blocks.Generator(pad_pos_list,cmd_label="pad")
  link(step_gen,gen_pad,condition=Bypass(bp_p2,{'step':len(state)-1}))

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

  link(speed_gen,labjack1)
  link(gen_fio2,labjack1)
  link(gen_fio3,labjack1)
  link(force_gen,labjack1)
  link(fmode_gen,labjack1)

  link(labjack1,speed_gen)
  link(labjack1,step_gen)

  # == And the associated saver
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
    c['range'] = int(1000*c['range']) # V to mV
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
    print("lj2Lablels=",lj2_labels)
    print("lj2 chan=",lj2)
    labjack2 = blocks.IOBlock("Labjack_t7",identifier="470014418",
        channels=lj2,labels=lj2_labels,freq=freq_lj2,verbose=True)

    # == And the saver
    lj2_saver = blocks.Saver(savepath+"lj2.csv")
    link(labjack2,lj2_saver)

  # Creating the graphs
  graphs = []
  for g in graph.values():
    print("Graph:",g)
    graphs.append(blocks.Grapher(*[('t(s)',lbl) for lbl in g],backend='qt4agg'))
    # Link to the concerned blocks
    if any([lbl in [c['lbl'] for c in spectrum] for lbl in g]):
      link(spectrum_block,graphs[-1],
        condition=HFSplit(spec_labels,spec_chan,spec_gains,spec_ranges))
    if any([lbl in lj2_labels for lbl in g]):
      link(labjack2,graphs[-1])
    if any([lbl in in_chan.keys() for lbl in g]):
      link(labjack1,graphs[-1])

  start()
