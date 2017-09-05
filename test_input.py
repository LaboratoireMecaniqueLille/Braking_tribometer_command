#coding: utf-8
from __future__ import print_function
import Tkinter as tk
import tkMessageBox

def goto(a,b=0):
  """Goto help...
  To do stuff

  Voilà"""
  return {'a':a,'b':b}

def slow(a,b=0):
  """Slow help
  To slow down to speed b

  Tadam"""
  return a,b

def read_ui(evt=None):
  global a
  try:
    a = flatten(eval(
        "["+",".join(ui.get("1.0",tk.END).strip().split("\n")).replace(",,",",")+"]"))
  except Exception as e:
    print("Error during eval():",e)
    tkMessageBox.showwarning("Invalid syntax",
        """The input is invalid, make sure that:
- All the <args> were replaced
- You did not leave blank lines
- All the requiered args are given
- There is no typo in the function names""")
    return
  print(a,len(a),type(a))

avail = [goto,slow]

def update_infos(event=None):
  #print("You chose",path_list.get(int(path_list.curselection()[0])))
  i = int(path_list.curselection()[0])
  s = proto(avail[i])
  s += "\n"+avail[i].__doc__.strip()
  help_label.configure(text=s)

def add_path(self):
  ui.insert(tk.END,"\n"+proto(avail[int(path_list.curselection()[0])]))

def flatten(l):
  """
  l is a list, if l contains lists, each item of this list
  will be inserted in l at the place where the list was
  Ex: [a,b,[c,d],e] => [a,b,c,d,e]
  NOTE: If l contains strings with [ or ] they will be removed but this is
  not the case here.
  (I am aware that this is extremely ugly and probably inefficient,
  but it is short and simple...)
  """
  return eval("["+str(l).replace("[","").replace("]","")+"]")

def proto(f):
  """To create a clean readable representation of the function"""
  l = ["<"+n+">" for n in f.func_code.co_varnames]
  if f.__defaults__:
    for i,d in enumerate(reversed(f.__defaults__)):
      l[-i-1] = l[-i-1][:-1] + "="+str(d)+">"
  return f.__name__ + "(" + ",".join(l) + ")"


root = tk.Tk()

ui = tk.Text(root)
ui.pack()

submit = tk.Button(root,text="Submit",command=read_ui)
submit.pack()

path_list = tk.Listbox(root)
path_list.pack()
path_list.insert(tk.END,*[f.__name__ for f in avail])
path_list.bind("<<ListboxSelect>>",update_infos)
path_list.bind("<Double-1>",add_path)

help_label = tk.Label(root,justify=tk.LEFT)
help_label.pack()


root.mainloop()
