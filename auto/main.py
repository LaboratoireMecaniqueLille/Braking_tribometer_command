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

root = tk.Tk()

help_txt = tk.Text(width=80,height=15)
help_txt.grid(row=2,column=0)

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
      + [d['lbl'] for d in spectrum_frame.chan_list]
  assert len(set(l)) == len(l),"Duplicate label!"
  return l

graph_frame = GraphFrame(root,get_labels)
graph_frame.grid(row=1,column=1)

frames = [path_frame,lj_frame,spectrum_frame,graph_frame]

load_frame = LoadFrame(root, frames)
load_frame.grid(row=2,column=1)

go = tk.Button(root,text="GO!")
go.grid(row=3,column=1)

root.mainloop()
