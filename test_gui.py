import crappy

#import matplotlib
#matplotlib.use("tkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg#, NavigationToolbar2TkAgg

from time import time

import Tkinter as tk

class Interface(crappy.blocks.MasterBlock):
  def __init__(self):
    crappy.blocks.MasterBlock.__init__(self)
    self.labels = ['t(s)','val']

  def prepare(self):
    self.root = tk.Tk()
    self.label = tk.Label(self.root)
    self.label.configure(text="Bonjour")
    self.label.pack()
    self.button = tk.Button(self.root,text="Bouton",command=self.inc)
    self.button.pack()
    self.root.protocol("WM_DELETE_WINDOW",self.end)
    self.value = 1
    self.f = plt.figure()
    self.ax = self.f.add_subplot(111)
    self.line, = self.ax.plot([],[])
    self.canvas = FigureCanvasTkAgg(self.f,master=self.root)
    self.canvas.show()
    self.canvas.get_tk_widget().pack()

  def inc(self):
    self.value += 1

  def handle_in(self,data):
    self.line.set_xdata(list(self.line.get_xdata())+data['t(s)'])
    self.line.set_ydata(list(self.line.get_ydata())+data['cmd'])
    self.canvas.draw()
    self.ax.relim()
    self.ax.autoscale_view(True, True, True)

  def loop(self):
    d = self.get_all_last()
    if any(d):
      self.handle_in(d)
    self.root.update()
    self.send([time()-self.t0,self.value])

  def end(self):
    self.root.destroy()
    self.stop_all()


g = crappy.blocks.Generator([{'type':'sine','amplitude':1,'freq':1,'condition':'delay=100'}])
gui = Interface()
crappy.link(g,gui)
graph = crappy.blocks.Grapher(('t(s)','val'))
crappy.link(gui,graph)

crappy.start()
