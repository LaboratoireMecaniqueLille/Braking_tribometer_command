#coding: utf-8
from __future__ import division, print_function

from crappy import blocks,start,condition,link

class Status_printer(blocks.MasterBlock):
  def __init__(self,d):
    blocks.MasterBlock.__init__(self)
    self.d = d

  def loop(self):
    print(self.d[self.inputs[0].recv()['step']])

def launch(path,spectrum,lj,graph):
  print("Let's go!",path,spectrum,lj,graph)

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
      state.append({'condition':'rpm(t/min)>'+str(.99*speed),'value':i})
    else:
      state.append({'condition':'rpm(t/min)<'+str(1.01*speed),'value':i})
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
    state.append({'condition':'rpm(t/min)<'+str(speed),'value':i})
    status_printer.append(
      "Breaking down to speed {} with inertia simulation".format(
      speed))
    speed_list.append({'type':'inertia','flabel':'C(Nm)','inertia':inertia,
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
    state.append({'condition':'rpm(t/min)<'+str(speed),'value':i})
    status_printer.append(
      "Breaking down to speed {} with inertia simulation".format(
      speed))
    speed_list.append({'type':'inertia','flabel':'C(Nm)','inertia':inertia,
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

  step_gen = blocks.Generator(state,cmd_label="step",verbose=True)
  sp = Status_printer(status_printer)
  link(step_gen,sp,condition=condition.Trig_on_change("step"))


  graph_step = blocks.Grapher(('t(s)','step'),backend="qt4agg")
  link(step_gen,graph_step)

  speed_gen = blocks.Generator(speed_list,cmd_label="speed_cmd",freq=400)
  link(step_gen,speed_gen,condition=condition.Trig_on_change("step"))

  force_gen = blocks.Generator(force_list,cmd_label="f_cmd")
  link(step_gen,force_gen,condition=condition.Trig_on_change("step"))

  fmode_gen = blocks.Generator(force_mode_list,cmd_label="fmode")
  link(step_gen,fmode_gen,condition=condition.Trig_on_change("step"))

  padpos_gen = blocks.Generator(pad_pos_list,cmd_label="pad")
  link(step_gen,padpos_gen,condition=condition.Trig_on_change("step"))

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

  gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='h2')
  gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='h3')

  gen_hydrau = blocks.Generator(hydrau_list,cmd_label="hydrau",cmd=1)
  link(gen_hydrau,gen_fio2)
  link(gen_hydrau,gen_fio3)
  link(step_gen,gen_hydrau,condition=condition.Trig_on_change("step"))

  gen_pad = blocks.Generator(pad_pos_list,cmd_label="pad")
  link(step_gen,gen_pad,condition=condition.Trig_on_change("step"))


  lj = blocks.IOBlock("Labjack_t7",identifier="470012972",channels=[
    {'name':'TDAC0','gain':1/412,'make_zero':False},
    {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
    {'name':'AIN1','gain':413,'make_zero':False}, # rpm
    {'name':'AIN2','gain':-50,'make_zero':True}, # torque
    {'name':'FIO2','direction':True}, # Hydrau
    {'name':'FIO3','direction':True}, # ..
    {'name':46000,'direction':True},
    {'name':46002,'direction':True},
    ],labels=['t(s)','F(N)','rpm(t/min)','C(Nm)'],
    cmd_labels=['speed_cmd','h2','h3','f_cmd','fmode'])

  link(speed_gen,lj)
  link(gen_fio2,lj)
  link(gen_fio3,lj)
  link(force_gen,lj)
  link(fmode_gen,lj)

  link(lj,speed_gen)
  link(lj,step_gen)


  servostar = blocks.Machine([{"type":"Servostar","cmd":"pad","mode":"position",
                              "device":"/dev/ttyS4"}])
  link(padpos_gen,servostar)
  graph = blocks.Grapher(('t(s)','F(N)'),('t(s)','rpm(t/min)'),backend="qt4agg")
  graphC = blocks.Grapher(('t(s)','C(Nm)'))
  link(lj,graphC)
  link(lj,graph)

  start()
