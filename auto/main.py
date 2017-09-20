#coding: utf-8

# ========================================
# = The main interface for the auto mode =
# ========================================

from __future__ import print_function

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

help_txt = tk.Text(width=80,height=15)
help_txt.grid(row=2,column=0)
d = []

def output(s):
  """
  To write s in the help_txt box.
  """
  help_txt.configure(state=tk.NORMAL)
  help_txt.delete("1.0",tk.END)
  help_txt.insert("1.0",s)
  help_txt.configure(state=tk.DISABLED)

root.output = output

path_frame = PathFrame(root)
path_frame.grid(row=0,column=0)

lj_frame = LJFrame(root)
lj_frame.grid(row=1,column=0)

spectrum_frame = SpectrumFrame(root)
spectrum_frame.grid(row=0,column=1)

def get_labels():
  l = [d['lbl'] for d in lj_frame.chan_list]\
      + [d['lbl'] for d in spectrum_frame.chan_list]\
      + in_chan.keys()
  duplicates = [lbl for i,lbl in enumerate(l) if lbl in l[:i]]
  if duplicates:
    output("Duplicate label(s): "+str(duplicates))
    return []
  return l

graph_frame = GraphFrame(root,get_labels)
graph_frame.grid(row=1,column=1)

frames = [path_frame,lj_frame,spectrum_frame,graph_frame]

load_frame = LoadFrame(root, frames)
load_frame.grid(row=2,column=1)

def go():
  d[:] = []
  d.append(path_frame.get_path())
  d.append(spectrum_frame.get_config())
  d.append(lj_frame.get_config())
  d.append(graph_frame.get_config())
  d.append(save_dir_entry.get())
  root.destroy()

go = tk.Button(root,text="GO!",command=go)
go.grid(row=3,column=2)

# Save dir
from tkFileDialog import askdirectory
def choose_dir():
  #global save_dir
  r = askdirectory()
  if r:
    #save_dir = r
    save_dir_entry.delete(0,tk.END)
    save_dir_entry.insert(0,r)

save_dir = '/home/tribo'
save_dir_entry = tk.Entry(root)
save_dir_entry.insert(0,save_dir)
save_dir_entry.grid(row=3,column=0)
save_dir_button = tk.Button(root,text="...",command=choose_dir)
save_dir_button.grid(row=3,column=1)


root.mainloop()

if d:
  e = list(d)
  launch(*e)
