#coding: utf-8
from __future__ import print_function, division
import warnings

from crappy import blocks, condition, start, link
warnings.filterwarnings("ignore",".*GUI is implemented.*")

# ========= Definition of the simples functions to expose to the user
def goto(speed,delay=5):
  return {'type':'goto','speed':speed,'delay':delay}

def slow(force,speed,inertia=10):
  return {'type':'slow','speed':speed,'force':force,'inertia':inertia}

def cst_f(force,delay):
  return {'type':'cst_F','force':force,'delay':delay}
# ======== Definition of the path by the user

path = [goto(5),slow(500,0),goto(500),cst_f(400,3),slow(500,0)]

path.append({'type':'ending'})

print("path=",path)
for d,n in zip(path[:-1],path[1:]):
  if not "force" in d:
    if "force" in n:
      d["force"] = n["force"]
    else:
      d["force"] = 0

print("path=",path)


# ===== Block that will simply print the status at each step in the terminal

class Status_printer(blocks.MasterBlock):
  def __init__(self,d):
    blocks.MasterBlock.__init__(self)
    self.d = d

  def loop(self):
    print(self.d[self.inputs[0].recv()['step']])

state = [] # Path for the state generator (increment after each substep)
speed = [] # Path for the motor
force = [] # Path for the pad analog input
force_mode = [] # Path for switching on and off the PID
pad_pos = [] # To control the pad mode and set the position
hydrau = [] # To drive the hydraulic actuator


status_printer = [] # List of each substep to print the current step


i = 0
last_step = {"speed":0}
for step in path:
  print(step)
  if step['type'] == 'goto':
    # Acceleration
    if last_step["speed"] < step["speed"]:
      state.append({'condition':'rpm(t/min)>'+str(.99*step['speed']),'value':i})
    else:
      state.append({'condition':'rpm(t/min)<'+str(1.01*step['speed']),'value':i})
    status_printer.append("Accelerating")
    i += 1
    # Stabilisation
    state.append({'condition':'delay='+str(step['delay']),'value':i})
    status_printer.append("Stabilisating speed")
    speed.append({'type':'constant','value':step['speed'],
                  'condition':'step>'+str(i)})
    #force.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    #force_mode.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    force.append({'type':'constant','value':step["force"],
                  'condition':'step>'+str(i)})
    force_mode.append({'type':'constant','value':1,'condition':'step>'+str(i)})

    if step["force"] != 0:
      pad_pos.append({'type':'constant','value':False,
                      'condition':'step>'+str(i)})
    else:
      pad_pos.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    hydrau.append({'type':'constant','value':1,'condition':'step>'+str(i)})
    i += 1
  elif step['type'] == 'slow':
    # Next step when we reach the lowest point
    state.append({'condition':'rpm(t/min)<'+str(step['speed']),'value':i})
    status_printer.append(
      "Breaking down to speed {} with inertia simulation".format(
      step['speed']))
    speed.append({'type':'inertia','flabel':'C(Nm)','inertia':step['inertia'],
                  'condition':'step>'+str(i)})
    force.append({'type':'constant','value':step['force'],
                  'condition':'step>'+str(i)})
    force_mode.append({'type':'constant','value':1,'condition':'step>'+str(i)})
    pad_pos.append({'type':'constant','value':False,'condition':'step>'+str(i)})
    hydrau.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    i+=1
  elif step['type'] == 'cst_F':
    state.append({'condition':'delay='+str(step['delay']),'value':i})
    status_printer.append("Breaking with constant force")
    speed.append({'type':'constant','condition':'step>'+str(i)})
    force.append({'type':'constant','value':step['force'],
                  'condition':'step>'+str(i)})
    force_mode.append({'type':'constant','value':1,'condition':'step>'+str(i)})
    pad_pos.append({'type':'constant','value':False,'condition':'step>'+str(i)})
    hydrau.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    i+=1
  elif step['type'] == 'ending':
    delay = 'delay=1'
    state.append({'condition':delay,'value':i})
    status_printer.append("End")
    speed.append({'type':'constant','value':0,'condition':delay})
    force.append({'type':'constant','value':0,'condition':delay})
    force_mode.append({'type':'constant','value':0,'condition':delay})
    pad_pos.append({'type':'constant','value':0,'condition':delay})
    hydrau.append({'type':'constant','value':0,'condition':delay})
  last_step = step


for d in state:
  d['type'] = 'constant'

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
display(speed)
print("Force:")
display(force)
print("Force mode:")
display(force_mode)
print("Pad pos:")
display(pad_pos)
print("Hydrau:")
display(hydrau)
#"""

step_gen = blocks.Generator(state,cmd_label="step",verbose=True)
sp = Status_printer(status_printer)
link(step_gen,sp,condition=condition.Trig_on_change("step"))


graph_step = blocks.Grapher(('t(s)','step'))
link(step_gen,graph_step)


speed_gen = blocks.Generator(speed,cmd_label="speed_cmd")
link(step_gen,speed_gen,condition=condition.Trig_on_change("step"))

force_gen = blocks.Generator(force,cmd_label="f_cmd")
link(step_gen,force_gen,condition=condition.Trig_on_change("step"))

fmode_gen = blocks.Generator(force_mode,cmd_label="fmode")
link(step_gen,fmode_gen,condition=condition.Trig_on_change("step"))

padpos_gen = blocks.Generator(pad_pos,cmd_label="pad")
link(step_gen,padpos_gen,condition=condition.Trig_on_change("step"))

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

gen_fio2 = blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='h2')
gen_fio3 = blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='h3')

gen_hydrau = blocks.Generator(hydrau,cmd_label="hydrau")
link(gen_hydrau,gen_fio2)
link(gen_hydrau,gen_fio3)
link(step_gen,gen_hydrau,condition=condition.Trig_on_change("step"))

gen_pad = blocks.Generator(pad_pos,cmd_label="pad")
link(step_gen,gen_pad,condition=condition.Trig_on_change("step"))


lj = blocks.IOBlock("Labjack_t7",identifier="470012972",channels=[
  {'name':'TDAC0','gain':1/412},
  {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
  {'name':'AIN1','gain':413,'make_zero':True}, # rpm
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

graph = blocks.Grapher(('t(s)','F(N)'),('t(s)','C(Nm)'),('t(s)','rpm(t/min)'))
link(lj,graph)

start()
