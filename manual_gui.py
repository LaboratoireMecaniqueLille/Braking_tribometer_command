#coding: utf-8
from __future__ import print_function,division

from time import sleep
import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import crappy

class Graph(object):
  def __init__(self,root,left=1,right=0):
    self.root = root
    self.fig, self.axl = plt.subplots()
    if right:
      self.axr = self.axl.twinx()
    self.axr.grid()
    self.axl.grid()
    self.rline = []
    self.lline = []

    for i in range(left):
      self.lline.append(self.axl.plot([],[])[0])
      # To avoid restarting the color cycle on the second y axis:
      next(self.axr._get_lines.color_cycle)
    for i in range(right):
      self.rline.append(self.axr.plot([],[])[0])
    self.canvas = FigureCanvasTkAgg(self.fig,master=root)
    self.canvas.show()
    plt.grid()

  def pack(self,*args,**kwargs):
    self.canvas.get_tk_widget().pack(*args,**kwargs)

  def grid(self,*args,**kwargs):
    self.canvas.get_tk_widget().grid(*args,**kwargs)

  def plot(self,x,y,num):
    if num >= len(self.lline):
      line = self.rline[num - len(self.lline)]
      ax = self.axr
    else:
      line = self.lline[num]
      ax = self.axl
    if isinstance(x,list):
      line.set_xdata(list(line.get_xdata())+x)
      line.set_ydata(list(line.get_ydata())+y)
    else:
      line.set_xdata(list(line.get_xdata())+[x])
      line.set_ydata(list(line.get_ydata())+[y])
    self.canvas.draw()
    ax.relim()
    ax.autoscale_view(True, True, True)


tempo_hydrau = .2
#lj1 = crappy.inout.Labjack_t7(identifier="470012972",
    #out_channels="TDAC0",out_gain=1/400) # T7
lj1 = crappy.inout.Labjack_t7(identifier="470012972",channels=[
  {'name':'TDAC0','gain':1/412},
  {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
  {'name':'AIN1','gain':413,'make_zero':False}, # rpm
  {'name':'AIN2','gain':-50,'make_zero':True}, # torque
  {'name':'FIO2','direction':True}, # Hydrau
  {'name':'FIO3','direction':True}, # ..
  ])
lj1.open()

def enable_pid():
  #if not lj1.read(6000):
  #  lj1.write(1,6000) # LUA_RUN
  lj1.write(1,46002)

def disable_pid():
  set_pid(0)
  lj1.write(0,46002)
  #if lj1.read(6000):
  #  lj1.write(0,6000) # LUA_RUN

def set_pid(val):
  lj1.write(val,46000)

servostar = crappy.actuator.Servostar('/dev/ttyS4')
servostar.open()

def update_servo_mode():
  if servo_mode.get() == 1:
    print("Setting to force mode")
    enable_pid()
    servostar.set_mode_analog()
  else:
    print("Setting to position mode")
    disable_pid()
    servostar.set_mode_serial()
  update_servo()

def update_servo(event=None):
  if servo_mode.get() == 1: # Force mode
    set_pid(float(servo_field.get()))
  else:
    servostar.set_position(int(float(servo_field.get())))

def update_speed(event=None):
  lj1.set_cmd(float(speed_field.get()))

def end(event=None):
  servostar.close()
  #lj1.close()
  root.destroy()

def update():
  pos_label.configure(text=str(servostar.get_position())+" µm")
  t,f,v,c = lj1.get_data()
  #print("DEBUG",t,f,v,c)
  graph.plot(t,f,0)
  graph.plot(t,v,1)
  graph.plot(t,c,2)
  root.after(50,update)

def hydrau_out():
  lj1["FIO2"] = 1
  lj1["FIO3"] = 1
  sleep(tempo_hydrau)
  lj1["FIO3"] = 0
  hydrau_label.configure(text="Hydrau out")

def hydrau_in():
  lj1["FIO2"] = 1 # Just to be sure...
  lj1["FIO3"] = 1
  sleep(tempo_hydrau)
  lj1["FIO2"] = 0
  sleep(tempo_hydrau)
  lj1["FIO3"] = 0
  hydrau_label.configure(text="Hydrau in")

root = tk.Tk()
root.protocol("WM_DELETE_WINDOW",end)


servo_mode = tk.IntVar(0)
servo_mode_radio = []
servo_mode_radio.append(tk.Radiobutton(root,
  variable=servo_mode,
  text="Position (µm)",
  command=update_servo_mode,
  value=0))
servo_mode_radio.append(tk.Radiobutton(root,
  variable=servo_mode,
  text="Effort via PID (N)",
  command=update_servo_mode,
  value=1))

for r in servo_mode_radio:
  r.grid()

servo_field = tk.Entry(root)
servo_field.grid()
servo_field.bind("<Return>",update_servo)
servo_field.bind("<KP_Enter>",update_servo)

pos_label = tk.Label(root)
pos_label.grid()

graph = Graph(root,2,1)
graph.grid()

speed_field = tk.Entry(root)
speed_field.grid()
speed_field.bind("<Return>",update_speed)
speed_field.bind("<KP_Enter>",update_speed)

hout_button = tk.Button(root,text="hydrau out",command=hydrau_out)
hout_button.grid()
hin_button = tk.Button(root,text="hydrau in",command=hydrau_in)
hin_button.grid()

clear_fault = tk.Button(root,text="clear faults",command=servostar.clear_errors)
clear_fault.grid()

hydrau_label = tk.Label(root)
hydrau_label.grid()


#hydrau_in()
root.after(50,update)
root.mainloop()
