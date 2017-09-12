#coding: utf-8

# ========================================
# = The main interface for the auto mode =
# ========================================

from __future__ import print_function

import pickle

import Tkinter as tk
from tkFileDialog import askopenfilename,asksaveasfilename
from path_frame import PathFrame
from spectrum_frame import SpectrumFrame
from lj_frame import LJFrame
from graph_frame import GraphFrame
from funcs import avail

root = tk.Tk()

help_txt = tk.Text(width=80,height=15)
help_txt.grid(row=2,column=0,columnspan=2)

def output(s):
  """
  To write s in the help_txt box.
  """
  help_txt.configure(state=tk.NORMAL)
  help_txt.delete("1.0",tk.END)
  help_txt.insert("1.0",s)
  help_txt.configure(state=tk.DISABLED)

root.output = output

path_frame = PathFrame(root,avail)
path_frame.grid(row=0,column=0)

lj_frame = LJFrame(root,
    [{'lbl':'T1','chan':'AIN0','range':10,'offset':0,'zero':False,'gain':1.5}])
lj_frame.grid(row=1,column=0)

spectrum_frame = SpectrumFrame(root,
    [{'lbl':'C(Nm)','chan':'1','range':10,'gain':2}])
spectrum_frame.grid(row=0,column=1)

def get_labels():
  l = [d['lbl'] for d in lj_frame.chan_list]\
      + [d['lbl'] for d in spectrum_frame.chan_list]
  assert len(set(l)) == len(l),"Duplicate label!"
  return l
test = {'Graph1':['C(Nm)'],'Graph2':['T1']}
graph_frame = GraphFrame(root,get_labels,test)
graph_frame.grid(row=1,column=1)

def load_conf():
  def load():
    path = askopenfilename(filetypes = (("Pickles","*.p"),("All files","*.*")))
    if not path:
      return
    with open(path,'rb') as f:
      try:
        config = pickle.load(f)
      except:
        output("Invalid file: "+path)
      #print(config)
    if var_path.get():
      #path_frame.textbox.delete("1.0",tk.END)
      #path_frame.textbox.insert("1.0",config["path"])
      path_frame.set_config(config['path'])
    if var_lj.get():
      lj_frame.listbox.delete(0,tk.END)
      for c in config['lj']:
        lj_frame.listbox.insert(tk.END,c['lbl']+": "+str(c['chan']))
      lj_frame.chan_list = config['lj']
    if var_spectrum.get():
      spectrum_frame.listbox.delete(0,tk.END)
      for c in config['spectrum']:
        spectrum_frame.listbox.insert(tk.END,c['lbl']+": "+str(c['chan']))
      spectrum_frame.chan_list = config['spectrum']
    if var_graph.get():
      #graph_frame.graph_dict = config['graph']
      #graph_frame.update_lists()
      graph_frame.set_config(config['graph'])
    top.destroy()
  top = tk.Toplevel()
  top.title("Load")
  var_path = tk.IntVar()
  check_path = tk.Checkbutton(top,text="Path",var=var_path)
  check_path.grid(row=1,column=0)
  var_lj = tk.IntVar()
  check_lj = tk.Checkbutton(top,text="Labjack",var=var_lj)
  check_lj.grid(row=2,column=0)
  var_spectrum = tk.IntVar()
  check_spectrum = tk.Checkbutton(top,text="Spectrum",var=var_spectrum)
  check_spectrum.grid(row=3,column=0)
  var_graph = tk.IntVar()
  check_graph = tk.Checkbutton(top,text="Graph",var=var_graph)
  check_graph.grid(row=4,column=0)
  cancel = tk.Button(top,text='Cancel',command=top.destroy)
  cancel.grid(row=5,column=0)
  ok = tk.Button(top,text='Ok',command=load)
  ok.grid(row=5,column=1)


def save_conf():
  def save():
    path = asksaveasfilename(filetypes = (("Pickles","*.p"),("All files","*.*")))
    if var_path.get():
      config["path"] = path_frame.textbox.get('1.0',tk.END)
    if var_lj.get():
      config['lj'] = lj_frame.chan_list
    if var_spectrum.get():
      config['spectrum'] = spectrum_frame.chan_list
    if var_graph.get():
      config['graph'] = graph_frame.graph_dict
    if not (path or config):
      return
    with open(path,'wb') as f:
      pickle.dump(config,f)
    top.destroy()
  config = {}
  top = tk.Toplevel()
  top.title("Save")
  var_path = tk.IntVar()
  check_path = tk.Checkbutton(top,text="Path",var=var_path)
  check_path.grid(row=1,column=0)
  var_lj = tk.IntVar()
  check_lj = tk.Checkbutton(top,text="Labjack",var=var_lj)
  check_lj.grid(row=2,column=0)
  var_spectrum = tk.IntVar()
  check_spectrum = tk.Checkbutton(top,text="Spectrum",var=var_spectrum)
  check_spectrum.grid(row=3,column=0)
  var_graph = tk.IntVar()
  check_graph = tk.Checkbutton(top,text="Graph",var=var_graph)
  check_graph.grid(row=4,column=0)
  cancel = tk.Button(top,text='Cancel',command=top.destroy)
  cancel.grid(row=5,column=0)
  ok = tk.Button(top,text='Ok',command=save)
  ok.grid(row=5,column=1)


load_button = tk.Button(root,text="Load",command=load_conf)
load_button.grid(row=3,column=0)
save_button = tk.Button(root,text="Save",command=save_conf)
save_button.grid(row=3,column=1)
root.mainloop()
