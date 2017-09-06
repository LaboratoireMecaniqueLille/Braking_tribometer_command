#coding: utf-8

import Tkinter as tk

HELP = """HELP:

The above frame is used to describe each step of the test.
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


class PathFrame(tk.Frame):
  def __init__(self,root,funcs,text=None):
    tk.Frame.__init__(self,root,borderwidth=2,relief=tk.GROOVE)
    self.root = root
    self.funcs = funcs
    self.textbox = tk.Text(self,width=80,height=10)
    self.textbox.grid(row=0,column=0,columnspan=3)
    self.path_list = tk.Listbox(self)
    self.path_list.grid(row=1,column=0,rowspan=2,sticky=tk.N)
    self.path_list.insert(tk.END,*[f.__name__ for f in self.funcs])
    self.path_list.bind("<<ListboxSelect>>",self.update_help)
    self.path_list.bind("<Double-1>",self.append_path)
    self.help_txt = tk.Text(self,width=60,height=10,
        state=tk.DISABLED,wrap=tk.WORD)
    self.help_txt.grid(row=1,column=1,columnspan=2)
    self.help_txt.bind("<1>",self.print_help)
    self.print_help()

    self.load_button = tk.Button(self,text="Load")
    self.save_button = tk.Button(self,text="Save")
    self.load_button.grid(row=2,column=1)
    self.save_button.grid(row=2,column=2)

  def update_help(self,event=None):
    i = self.path_list.curselection()[0]
    s = proto(self.funcs[i])
    s += "\n"+self.funcs[i].__doc__.strip()
    self.set_help(s)

  def append_path(self,event=None):
    i = self.path_list.curselection()[0]
    self.textbox.insert(tk.END,"\n"+proto(self.funcs[i]))

  def print_help(self,event=None):
    self.set_help(HELP)

  def set_help(self,s):
    self.help_txt.configure(state=tk.NORMAL)
    self.help_txt.delete("1.0",tk.END)
    self.help_txt.insert("1.0",s)
    self.help_txt.configure(state=tk.DISABLED)
