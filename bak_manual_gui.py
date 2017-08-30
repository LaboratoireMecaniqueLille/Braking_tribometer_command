#coding: utf-8
from __future__ import print_function,division

import Tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import crappy

class Graph(object):
  def __init__(self,root):
    self.root = root
    self.f = plt.figure()
    self.ax = self.f.add_subplot(111)
    self.line, = self.ax.plot([],[])
    self.canvas = FigureCanvasTkAgg(self.f,master=root)
    self.canvas.show()

  def pack(self,*args,**kwargs):
    self.canvas.get_tk_widget().pack(*args,**kwargs)

  def grid(self,*args,**kwargs):
    self.canvas.get_tk_widget().grid(*args,**kwargs)

  def plot(self,x,y):
    if isinstance(x,list):
      self.line.set_xdata(list(self.line.get_xdata())+x)
      self.line.set_ydata(list(self.line.get_ydata())+y)
    else:
      self.line.set_xdata(list(self.line.get_xdata())+[x])
      self.line.set_ydata(list(self.line.get_ydata())+[y])
    self.canvas.draw()
    self.ax.relim()
    self.ax.autoscale_view(True, True, True)




#lj1 = crappy.inout.Labjack_t7(identifier="470012972",
    #out_channels="TDAC0",out_gain=1/400) # T7
lj1 = crappy.inout.Labjack_t7(identifier="470012972",channels=[
  {'name':'TDAC0','gain':1/412},
  {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
  {'name':'AIN1','gain':413,'make_zero':True}, # rpm
  {'name':'AIN2','gain':-500,'make_zero':True}, # torque
  ])
lj1.open()

def enable_pid():
  lj1.write(1,46002)

def disable_pid():
  set_pid(0)
  lj1.write(0,46002)

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
  root.after(50,update)
  t,f,v,c = lj1.get_data()
  #print("DEBUG",t,f,v,c)
  graph_f.plot(t,f)
  graph_v.plot(t,v)

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

pos_label = tk.Label(root)
pos_label.grid()

graph_f = Graph(root)
graph_f.grid()

graph_v = Graph(root)
graph_v.grid()

speed_field = tk.Entry(root)
speed_field.grid()
speed_field.bind("<Return>",update_speed)

root.after(50,update)
root.mainloop()
