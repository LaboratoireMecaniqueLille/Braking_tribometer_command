#coding: utf-8
from __future__ import print_function

__all__ = ["goto","wait","slow","slow_p","cst_f","cst_p","cst_c","wait_cd","funcs"]

# ========= Definition of the simples functions to expose to the user
def goto(speed,delay=5):
  """
Will accelerate to the given speed in rpm.

Once reached, it will wait <delay> seconds until next step starts.
This allows for the speed to stabilize before starting the next step.
The hydraulic actuator will be out to prevent the pad to touch
the disc during this phase.
"""
  return {'type':'goto','speed':speed,'delay':delay}

def make_goto(speed,delay,force=0,pos=0):
  i = len(paths['state'])
  # Acceleration
  if last_step["speed"] < speed:
    paths['state'].append(
        {'condition':'lj1_rpm(t/min)>'+str(.99*speed),'value':i})
  else:
    paths['state'].append(
        {'condition':'lj1_rpm(t/min)<'+str(1.01*speed),'value':i})
  paths['status'].append("Accelerating to %d rpm"%speed)
  i += 1
  # Stabilisation
  paths['state'].append({'condition':'delay='+str(delay),'value':i})
  paths['status'].append("Stabilisating speed (%ds)"%delay)
  # Common path (for acceleration and stabilisation)
  paths['speed'].append({'type':'constant','value':speed,
                'condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':force,
                'condition':'step>'+str(i)})
  paths['fmode'].append({'type':'constant','value':int(bool(force)),
                      'condition':'step>'+str(i)})
  if force != 0:
    paths['pad'].append({'type':'constant','value':False,
                    'condition':'step>'+str(i)})
  else:
    paths['pad'].append(
        {'type':'constant','value':pos,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})

def wait(delay):
  """
Will simply wait <delay> seconds
"""
  return {'type':'wait','delay':delay}

def make_wait(delay,force=0,pos=0):
  i = len(paths['state'])
  paths['state'].append({'condition':'delay='+str(delay),'value':i})
  paths['status'].append("Waiting %d s..."%delay)
  paths['speed'].append({'type':'constant', 'condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':force,
                'condition':'step>'+str(i)})
  paths['fmode'].append({'type':'constant','value':int(bool(force)),
                      'condition':'step>'+str(i)})
  if force != 0:
    paths['pad'].append({'type':'constant','value':False,
                    'condition':'step>'+str(i)})
  else:
    paths['pad'].append(
        {'type':'constant','value':pos,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})

def slow(force,inertia=5,speed=0): #inertia in kgm², speed in rpm
  """
Will simulate a breaking with an inertia of <inertia> kg.m² and <force> N.

The next step will start when the speed goes below <speed> (in rpm).
The pad normal force will be adjusted in real time with a PID.
"""
  return {'type':'slow','speed':speed,'force':force,'inertia':inertia}

def make_slow(force,inertia,speed):
  # Next step when we reach the lowest point
  i = len(paths['state'])
  paths['state'].append({'condition':'lj1_rpm(t/min)<'+str(speed),'value':i})
  paths['status'].append(
    "Breaking down to {} rpm with {} N and {} Nm² inertia simulation".format(
    speed,force,inertia))
  paths['speed'].append({'type':'inertia','flabel':'lj1_C(Nm)',
                'inertia':inertia, 'condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':force,
                'condition':'step>'+str(i)})
  paths['fmode'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})
  paths['pad'].append(
      {'type':'constant','value':False,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})

def slow_p(pos,inertia=5,speed=0):
  """
Will simulate a breaking with an inertia of <inertia> kg.m².

The force PID will be disabled and instead the pad motor will
stay at the given position (in µm).
Note that lower values mean higher force: you should
enter a negative value for a positive force.
The next step will start when the speed goes below <speed> (in rpm).
"""
  return {'type':'slow_p','speed':speed,'pos':pos,'inertia':inertia}

def make_slowp(pos,inertia,speed):
  # Next step when we reach the lowest point
  i = len(paths['state'])
  paths['state'].append({'condition':'lj1_rpm(t/min)<'+str(speed),'value':i})
  paths['status'].append(
    "Breaking down to {} rpm with {} µm and {} Nm² inertia simulation".format(
    speed,pos,inertia))
  paths['speed'].append({'type':'inertia','flabel':'lj1_C(Nm)',
                'inertia':inertia, 'condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':0,
                'condition':'step>'+str(i)})
  paths['fmode'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})
  paths['pad'].append(
      {'type':'constant','value':pos,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})

def cst_f(force,delay):
  """
Will apply a constant force on the pad without changing the speed of the disc

The next step will start after <delay> seconds
The pad normal force will be adjusted in real time with a PID.
"""
  return {'type':'cst_F','force':force,'delay':delay}

def make_cstf(force,delay):
  i = len(paths['state'])
  paths['state'].append({'condition':'delay='+str(delay),'value':i})
  paths['status'].append("Breaking with constant force of %d N for %ds"%(
    force,delay))
  paths['speed'].append({'type':'constant','condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':force,
                'condition':'step>'+str(i)})
  paths['fmode'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})
  paths['pad'].append(
      {'type':'constant','value':False,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})

def cst_c(torque,delay):
  """
Will try to apply a constant torque on the axis (at constant speed).

The next step will start after <delay> seconds
The pad force will be adjusted to through a PID to get the torque
to the given value.
Make sure that the disc is rotating or the force will increase undefinitely!
"""
  return {'type':'cst_C','torque':torque,'delay':delay}

def make_cstc(torque,delay):
  i = len(paths['state'])
  paths['state'].append({'condition':'delay='+str(delay),'value':i})
  paths['status'].append("Breaking with constant torque of %d Nm for %d s"%(
    torque,delay))
  paths['speed'].append({'type':'constant','condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':torque,
                'condition':'step>'+str(i)})
  paths['fmode'].append(
      {'type':'constant','value':2,'condition':'step>'+str(i)})
  paths['pad'].append(
      {'type':'constant','value':False,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})

def cst_p(pos,delay):
  """
To apply a force without the PID, the speed stays constant.

The next step will start after <delay> seconds
The pad motor will stay at the given position and the speed will not vary.
"""
  return {'type':'cst_P','pos':pos,'delay':delay}

def make_cstp(pos,delay):
  i = len(paths['state'])
  paths['state'].append({'condition':'delay='+str(delay),'value':i})
  paths['status'].append("Breaking with constant position of %d µm for %d s"%(
    pos,delay))
  paths['speed'].append({'type':'constant','condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':0,
                'condition':'step>'+str(i)})
  paths['fmode'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})
  paths['pad'].append(
      {'type':'constant','value':pos,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':0,'condition':'step>'+str(i)})

def wait_cd(s):
  """
To wait for a sensor do go past/below a given value

It takes a single string as an argument.
The syntax is "mylabel[</>]value"
"""
  return {'type':'wait_cd','value':s}

def make_wait_cd(value,force=0,pos=0):
  i = len(paths['state'])
  paths['state'].append({'condition':value,'value':i})
  paths['status'].append("Waiting until "+value)
  paths['speed'].append({'type':'constant', 'condition':'step>'+str(i)})
  paths['force'].append({'type':'constant','value':force,
                'condition':'step>'+str(i)})
  paths['fmode'].append({'type':'constant','value':int(bool(force)),
                      'condition':'step>'+str(i)})
  if force != 0:
    paths['pad'].append({'type':'constant','value':False,
                    'condition':'step>'+str(i)})
  else:
    paths['pad'].append(
        {'type':'constant','value':pos,'condition':'step>'+str(i)})
  paths['hydrau'].append(
      {'type':'constant','value':1,'condition':'step>'+str(i)})

def make_end():
  delay = 'delay=1'
  paths['state'].append({'condition':delay,'value':len(paths['state'])})
  paths['status'].append("End")
  paths['speed'].append({'type':'constant','value':0,'condition':delay})
  paths['force'].append({'type':'constant','value':0,'condition':delay})
  paths['fmode'].append({'type':'constant','value':0,'condition':delay})
  paths['pad'].append({'type':'constant','value':0,'condition':delay})
  paths['hydrau'].append({'type':'constant','value':1,'condition':delay})

# ==================

funcs = [goto,wait,slow,slow_p,cst_f,cst_c,cst_p,wait_cd]
# ==== The functions that will turn each path into the path for the actuators

avail = {'goto':make_goto,
         'wait':make_wait,
         'slow':make_slow,
         'slow_p':make_slowp,
         'cst_F':make_cstf,
         'cst_C':make_cstc,
         'cst_P':make_cstp,
         'wait_cd':make_wait_cd,
         'end':make_end}

paths = {}
last_step = {"speed":0}

def prepare_path(path):
  for s in ['state','speed','force','fmode','pad','hydrau','status']:
    paths[s] = []
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

  # === Calling these functions according to the user input ====
  for step in path:
    t = step.pop("type")
    if t in avail:
      avail[t](**step)
    else:
      print("Unknown path:",t)
    last_step.update(step)

  # The state generator only uses constants
  for d in paths['state']:
    d['type'] = 'constant'

  # ==== Facultative: display path for debug =====
  #"""
  def display_state():
    for d,s in zip(paths['state'],paths['status']):
      print(" ",s)
      print("  ",d)

  def display(l):
    for d in l:
      print(" ",d)

  print("State:")
  display_state()
  print("Speed:")
  display(paths["speed"])
  print("Force:")
  display(paths["force"])
  print("Force mode:")
  display(paths["fmode"])
  print("Pad pos:")
  display(paths['pad'])
  print("Hydrau:")
  display(paths['hydrau'])
  #"""
  return paths
