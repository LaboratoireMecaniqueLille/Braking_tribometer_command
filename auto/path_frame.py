#coding: utf-8

import Tkinter as tk

from funcs import avail

HELP = """This frame is used to describe each step of the test.
You can use the functions in the list, click them to have a help message.
Double click to automatically add them at the end.
Some arguments are facultative and can be omitted
(the ones with a default value).
You can separate each call by a newline or a comma ','.
Do not skip multiple lines between functions
You can append N times a succession of functions using this syntax:
  [func1(args),func2(args),...]*N
"""

def proto(f):
  """To create a clean readable representation of the function

  Ex: myfunc(<arg1>,<arg2>,<arg3=None>)"""
  l = ["<"+n+">" for n in f.func_code.co_varnames]
  if f.__defaults__:
    for i,d in enumerate(reversed(f.__defaults__)):
      l[-i-1] = l[-i-1][:-1] + "="+str(d)+">"
  return f.__name__ + "(" + ",".join(l) + ")"

def flatten(l):
  """
  l is a list, if l contains lists, each item of this list
  will be inserted in l at the place where the list was
  Ex: [a,b,[c,d],e] => [a,b,c,d,e]
  NOTE: If l contains strings with [ or ] they will be removed but this is
  not the case here.
  (I am aware that this is extremely ugly and probably inefficient,
  but it is short, simple and works for what we are doing...)
  """
  return eval("["+str(l).replace("[","").replace("]","")+"]")

class PathFrame(tk.Frame):
  """
  This frame holds all the widgets to manage the path for the test.
  """
  def __init__(self,root,text=None):
    tk.Frame.__init__(self,root,borderwidth=2,relief=tk.GROOVE)
    self.root = root
    self.out = root.output
    self.funcs = avail
    self.textbox = tk.Text(self,width=50,height=10)
    self.textbox.grid(row=0,column=0)
    self.textbox.bind('<1>',lambda *a: self.out(HELP))
    self.path_list = tk.Listbox(self)
    self.path_list.grid(row=0,column=1)
    self.path_list.insert(tk.END,*[f.__name__ for f in self.funcs])
    self.path_list.bind("<<ListboxSelect>>",self.update_help)
    self.path_list.bind("<Double-1>",self.append_path)
    if text:
      self.set_config(text)

  def update_help(self,event=None):
    """
    Callback for selection of path in path_list.

    Gets the selected function and prints associated help in help_txt.
    """
    i = self.path_list.curselection()[0]
    s = proto(self.funcs[i])
    s += "\n"+self.funcs[i].__doc__.strip()
    self.out(s)

  def append_path(self,event=None):
    """
    Callback for double click on path in path_list.

    Will insert the selected path at the end of the textbox.
    """
    i = self.path_list.curselection()[0]
    self.textbox.insert(tk.END,proto(self.funcs[i])+"\n")

  def get_path(self):
    try:
      a = flatten(eval("["+",".join(self.textbox.get(
        "1.0",tk.END).strip().split("\n")).replace(",,",",")+"]"))
    except Exception as e:
      print("Error during eval():",e)
      a = None
    return a

  def get_config(self):
    self.get_path() # To make sure the path is correct
    return self.textbox.get("1.0",tk.END)

  def set_config(self,config):
    self.textbox.delete("1.0",tk.END)
    self.textbox.insert(tk.END,config)
