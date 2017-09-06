#coding: utf-8

# ========= Definition of the simples functions to expose to the user
def goto(speed,delay=5):
  """
Will accelerate to the given speed in rpm

Once reached, it will wait <delay> seconds until next step starts
The hydraulic actuator will be out to prevent the pad to touch
the disc during this phase.
"""
  return {'type':'goto','speed':speed,'delay':delay}

def wait(delay):
  """
Will simply wait <delay> seconds
"""
  return {'type':'wait','delay':delay}

def slow(force,inertia=5,speed=0): #inertia in kgm², speed in rpm
  """
Will simulate a breaking with an inertia of <inertia> kg.m² and <force> N

The next step will start when the speed goes below <speed> (in rpm)
"""
  return {'type':'slow','speed':speed,'force':force,'inertia':inertia}

def slow_p(pos,inertia=5,speed=0):
  """a
"""
  return {'type':'slow_p','speed':speed,'pos':pos,'inertia':inertia}

def cst_f(force,delay):
  """
cstf
"""
  return {'type':'cst_F','force':force,'delay':delay}

def cst_c(torque,delay):
  """
cstc
"""
  return {'type':'cst_C','torque':torque,'delay':delay}

def cst_p(pos,delay):
  """cstp
"""
  return {'type':'cst_P','pos':pos,'delay':delay}
# ==================

avail = [goto,wait,slow,slow_p,cst_f,cst_c,cst_p]
