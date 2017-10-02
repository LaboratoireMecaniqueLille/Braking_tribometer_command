#coding: utf-8

# ========================================
# = The main interface for the auto mode =
# ========================================

from __future__ import print_function

from time import ctime
import Tkinter as tk

# Frames
from path_frame import PathFrame
from spectrum_frame import SpectrumFrame
from lj_frame import LJFrame
from graph_frame import GraphFrame
from load_frame import LoadFrame

from launch import launch
from lj1_chan import in_chan

root = tk.Tk()

# This widget is used to display help messages and errors
help_txt = tk.Text(width=80,height=15)
help_txt.grid(row=2,column=0,columnspan=2)
d = []

# This function is meant to print a message in the help widget
def output(s):
  """
  To write s in the help_txt box.
  """
  help_txt.configure(state=tk.NORMAL)
  help_txt.delete("1.0",tk.END)
  help_txt.insert("1.0",s)
  help_txt.configure(state=tk.DISABLED)

# Hack to send the output function to all widgets
root.output = output

# == Creating the main frames ==
path_frame = PathFrame(root)
path_frame.grid(row=0,column=0,columnspan=2)

lj_frame = LJFrame(root)
lj_frame.grid(row=1,column=0,columnspan=2)

spectrum_frame = SpectrumFrame(root)
spectrum_frame.grid(row=0,column=2)

# The graph frame needs a way to know the name of the available labels
def get_labels():
  """
  Returns a list of the labels that one can plot

  It is a list of str, regrouping the labels of the spectrum channels,
  the Labjack2 channels (added via the GUI) and the control Labjack.
  """
  l = [d['lbl'] for d in lj_frame.chan_list]\
      + [d['lbl'] for d in spectrum_frame.chan_list]\
      + in_chan.keys()
  duplicates = [lbl for i,lbl in enumerate(l) if lbl in l[:i]]
  if duplicates:
    output("Duplicate label(s): "+str(duplicates))
    return []
  return l

graph_frame = GraphFrame(root,get_labels)
graph_frame.grid(row=1,column=2)

frames = [path_frame,lj_frame,spectrum_frame,graph_frame]

load_frame = LoadFrame(root, frames)
load_frame.grid(row=2,column=2)

# == Creating the GO button and its callback ==
def go():
  d[:] = []
  try:
    d.append(path_frame.get_path())
    d.append(spectrum_frame.get_config())
    d.append(lj_frame.get_config())
    enable_drawing, graph_frame_config = graph_frame.get_config()
    d.append(graph_frame_config)
    save_dir = save_dir_entry.get()
    if save_dir[-1] != "/":
      save_dir += "/"
    save_dir += ctime()[:-5].replace(" ","_")+"/"
    d.append(save_dir)
    d.append(enable_drawing)
    load_frame.save_conf(save_dir+"config.p")
  except Exception,e:
    output(e)
    d[:] = []
    return
  root.destroy()

tk.Button(root,text="GO!",command=go).grid(row=3,column=2)

# == Creating the field to choose the save directory and its callback ==
def choose_dir():
  from tkFileDialog import askdirectory
  r = askdirectory()
  if r:
    save_dir_entry.delete(0,tk.END)
    save_dir_entry.insert(0,r)

save_dir = '/home/tribo/Bureau/essais'
save_dir_entry = tk.Entry(root)
save_dir_entry.insert(0,save_dir)
save_dir_entry.grid(row=3,column=0)
save_dir_button = tk.Button(root,text="...",command=choose_dir)
save_dir_button.grid(row=3,column=1)

# == And go! ==
root.mainloop()

# == The user has now closed the window, my work as a GUI is over ==
# If d is not empty (ie the user clicked GO), we copy it (just in case)
# and launch the test itself.
# To know what happens now, go to launch.py
if d:
  e = list(d)
  launch(*e)
