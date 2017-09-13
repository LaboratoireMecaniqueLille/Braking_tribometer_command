#coding: utf-8
__all__ = ["goto","wait","slow","slow_p","cst_f","cst_p","cst_c","avail"]

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

def wait(delay):
  """
Will simply wait <delay> seconds
"""
  return {'type':'wait','delay':delay}

def slow(force,inertia=5,speed=0): #inertia in kgm², speed in rpm
  """
Will simulate a breaking with an inertia of <inertia> kg.m² and <force> N.

The next step will start when the speed goes below <speed> (in rpm).
The pad normal force will be adjusted in real time with a PID.
"""
  return {'type':'slow','speed':speed,'force':force,'inertia':inertia}

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

def cst_f(force,delay):
  """
Will apply a constant force on the pad without changing the speed of the disc

The next step will start after <delay> seconds
The pad normal force will be adjusted in real time with a PID.
"""
  return {'type':'cst_F','force':force,'delay':delay}

def cst_c(torque,delay):
  """
Will try to apply a constant torque on the axis (at constant speed).

The next step will start after <delay> seconds
The pad force will be adjusted to through a PID to get the torque
to the given value.
Make sure that the disc is rotating or the force will increase undefinitely!
"""
  return {'type':'cst_C','torque':torque,'delay':delay}

def cst_p(pos,delay):
  """
To apply a force without the PID, the speed stays constant.

The next step will start after <delay> seconds
The pad motor will stay at the given position and the speed will not vary.
"""
  return {'type':'cst_P','pos':pos,'delay':delay}
# ==================

avail = [goto,wait,slow,slow_p,cst_f,cst_c,cst_p]
