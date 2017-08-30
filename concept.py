#coding: utf-8

from random import random
import crappy
import warnings
warnings.filterwarnings("ignore",".*GUI is implemented.*")

def disp(arg):
  print(arg)
  return arg

# ========= Definition of the simples functions to expose to the user
def goto(speed,delay=2):
  return {'type':'goto','speed':speed,'delay':delay}

def slow(force,speed,inertia=10):
  return {'type':'slow','speed':speed,'force':force,'inertia':inertia}

def cst_f(force,delay):
  return {'type':'cst_F','force':force,'delay':delay}
# ======== Definition of the path by the user

path = [goto(500),slow(500,200),goto(500),cst_f(400,3),slow(500,0)]

path.append({'type':'ending'})


# ===== Conditions for simulation (for testing without the actuators)
class Noise():
  def __init__(self,amplitude,label):
    self.amp = 2*amplitude
    self.lbl = label

  def evaluate(self,data):
    data[self.lbl] += (random()-.5)*self.amp
    return data

class Delay():
  def __init__(self,delay):
    self.delay = delay
    self.hist = []

  def evaluate(self,data):
    self.hist.append(data)
    if len(self.hist) > self.delay:
      return self.hist.pop(0)

# ===== Block that will simply print the status at each step in the terminal

class Status_printer(crappy.blocks.MasterBlock):
  def __init__(self,d):
    crappy.blocks.MasterBlock.__init__(self)
    self.d = d

  def loop(self):
    print(self.d[self.inputs[0].recv()['step']])


#======= definition of the lists of paths for each Generator


state = []
speed = []
force = []
hydrau = []
status_printer = []

i=0
for step in path:
  print(step)
  if step['type'] == 'goto':
    # Acceleration
    state.append({'condition':'rpm>'+str(.99*step['speed']),'value':i})
    status_printer.append("Accelération")
    i += 1
    # Stabilisation
    state.append({'condition':'delay='+str(step['delay']),'value':i})
    status_printer.append("Stabilisation")
    speed.append({'type':'constant','value':step['speed'],
                  'condition':'step>'+str(i)})
    force.append({'type':'constant','value':0,'condition':'step>'+str(i)})
    i += 1
  elif step['type'] == 'slow':
    # Next step until we reach the lowest point
    state.append({'condition':'rpm<'+str(step['speed']),'value':i})
    status_printer.append("Freinage simulation inertie jusqu'à {} rpm".format(
      step['speed']))
    speed.append({'type':'inertia','flabel':'force','inertia':step['inertia'],
                  'condition':'step>'+str(i)})
    force.append({'type':'constant','value':step['force'],
                  'condition':'step>'+str(i)})
    i+=1
  elif step['type'] == 'cst_F':
    state.append({'condition':'delay='+str(step['delay']),'value':i})
    status_printer.append("Freinage F cte")
    speed.append({'type':'constant','condition':'step>'+str(i)})
    force.append({'type':'constant','value':step['force'],
                  'condition':'step>'+str(i)})
    i+=1
  elif step['type'] == 'ending':
    delay = 'delay=1'
    state.append({'condition':delay,'value':i})
    status_printer.append("Fin")
    speed.append({'type':'constant','value':0,'condition':delay})
    force.append({'type':'constant','value':0,'condition':delay})


for d in state:
  d['type'] = 'constant'

print("State:",state)
print("Speed:",speed)


# ===== Creating and linking crappy blocks


state_g = crappy.blocks.Generator(state,cmd_label='step')
gg = crappy.blocks.Grapher(('t(s)','step'))
crappy.link(state_g,gg)

speed_g = crappy.blocks.Generator(speed,cmd_label='speed')
gs = crappy.blocks.Grapher(('t(s)','speed'))
crappy.link(speed_g,gs)

crappy.link(state_g,speed_g)


force_g = crappy.blocks.Generator(force,cmd_label='force',spam=True)
fg = crappy.blocks.Grapher(('t(s)','force'))
crappy.link(force_g,fg)
crappy.link(force_g,speed_g)
crappy.link(state_g,force_g)

pid = crappy.blocks.PID(kp=.03,
                        ki=.28,
                        kd=.015,
                        out_max=10,
                        out_min=-10,
                        input_label='rpm',
                        target_label='speed')

mot = crappy.blocks.Machine([{'type':'Fake_motor',
                             'cmd':'pid',
                             'mode':'speed',
                             'speed_label':'rpm',
                             # Motor properties:
                             'kv':1200,
                             'inertia':6,
                             'rv':.2,
                             'fv':1e-5
                             }])
crappy.link(pid,mot)
crappy.link(mot,pid)
crappy.link(speed_g,pid)
gmot = crappy.blocks.Grapher(('t(s)','rpm'))
crappy.link(mot,gmot)

crappy.link(mot,state_g)


sp = Status_printer(status_printer)
crappy.link(state_g,sp)

crappy.start()
