#coding: utf-8
from __future__ import print_function

from os import path
import pickle

import Tkinter as tk
from tkFileDialog import askopenfilename,asksaveasfilename

default_file = path.join(path.dirname(path.abspath(__file__)),"default.p")

class LoadFrame(tk.Frame):
  def __init__(self,root,frames):
    tk.Frame.__init__(self,root)
    self.out = root.output
    self.frames = frames
    self.load_button = tk.Button(self,text="Load",command=self.load_conf)
    self.load_button.grid(row=0,column=0)
    self.save_button = tk.Button(self,text="Save",command=self.save_conf)
    self.save_button.grid(row=1,column=0)
    try:
      self.load_conf(default_file)
    except:
      print("Could not load default config: "+default_file)
      self.out("Could not load default config: "+default_file)

  def load_conf(self,path=None):
    def load(path=None):
      auto = True
      if not path:
        path = askopenfilename(filetypes=(("Pickles","*.p"),
          ("All files","*.*")))
        auto = False
        if not path:
          return
      with open(path,'rb') as f:
        try:
          config = pickle.load(f)
        except:
          self.out("Invalid file: "+path)
          if not auto:
            top.destroy()
      not_ok = []
      for f in self.frames:
        if auto or check_vars[f.name].get():
          if f.name in config:
            r = f.set_config(config[f.name])
            if r:
              self.out(r) # To print an error if any
              return
          else:
            not_ok.append(f.name)
      if not_ok:
        self.out("Warning! This config file does NOT contain config for "\
            +str(not_ok))
      else:
        self.out("Successfully loaded config for "+str(config.keys())
            +" from "+str(path))
      if not auto:
        top.destroy()
    if path:
      load(path)
      return
    top = tk.Toplevel()
    top.title("Load")
    check_vars = {}
    for i,f in enumerate(self.frames):
      check_vars[f.name] = tk.IntVar()
      check_vars[f.name].set(1)
      tk.Checkbutton(top,text=f.name.capitalize(),
          var=check_vars[f.name]).grid(row=i,column=0)
    tk.Button(top,text="Load",command=load).grid(row=i+1,column=0)

  def save_conf(self):
    def save():
      path = asksaveasfilename(filetypes=(("Pickles","*.p"),
        ("All files","*.*")))
      if not path:
        return
      config = {}
      for f in self.frames:
        if check_vars[f.name]:
          config[f.name] = f.get_config()
      with open(path,'wb') as f:
        pickle.dump(config,f)
      self.out("Successfully saved config at "+path)
      top.destroy()
    top = tk.Toplevel()
    top.title("Save")
    check_vars = {}
    for i,f in enumerate(self.frames):
      check_vars[f.name] = tk.IntVar()
      check_vars[f.name].set(1)
      tk.Checkbutton(top,text=f.name.capitalize(),
          var=check_vars[f.name]).grid(row=i,column=0)
    tk.Button(top,text="Save",command=save).grid(row=i+1,column=0)
