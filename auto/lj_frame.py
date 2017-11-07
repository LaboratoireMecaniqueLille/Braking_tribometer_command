#coding: utf-8

import Tkinter as tk

class LJFrame(tk.Frame):
  def __init__(self,root):
    tk.Frame.__init__(self,root,borderwidth=2,relief=tk.RIDGE,
        height=350,width=600)
    self.name = "lj"
    self.root = root
    self.title = tk.Label(self,text="Labjack",
        font=("Helvetica",20))
    self.title.grid(row=0,column=0,columnspan=10)
    self.out = self.root.output
    self.listbox = tk.Listbox(self)
    self.listbox.grid(row=1,column=3,rowspan=4,columnspan=2)
    self.add_button = tk.Button(self,text="->",command=self.add_chan)
    self.add_button.grid(row=2,column=2)
    self.edit_button = tk.Button(self,text="<-",command=self.edit_chan)
    self.edit_button.grid(row=3,column=2)
    self.del_button = tk.Button(self,text="Delete",command=self.del_chan)
    self.del_button.grid(row=6,column=4)
    self.chan_list = []

    tk.Label(self,text="Label").grid(row=1,column=0)
    self.t_lbl = tk.Entry(self)
    self.t_lbl.grid(row=1,column=1)

    tk.Label(self,text="Channel").grid(row=2,column=0)
    self.t_chan= tk.Entry(self)
    self.t_chan.grid(row=2,column=1)

    tk.Label(self,text="Range").grid(row=3,column=0)
    self.t_range = tk.Entry(self)
    self.t_range.grid(row=3,column=1)

    tk.Label(self,text="Gain").grid(row=4,column=0)
    self.t_gain = tk.Entry(self)
    self.t_gain.grid(row=4,column=1)

    tk.Label(self,text="Offset").grid(row=5,column=0)
    self.t_offset = tk.Entry(self)
    self.t_offset.grid(row=5,column=1)

    tk.Label(self,text="Make zero?").grid(row=6,column=0)
    self.c_zero_var = tk.IntVar()
    self.c_zero = tk.Checkbutton(self,variable=self.c_zero_var)
    self.c_zero.grid(row=6,column=1)

    tk.Label(self,text="Frequency (Hz)").grid(row=7,column=1)
    self.freq_entry = tk.Entry(self,width=8)
    self.freq_entry.insert(0,"200")
    self.freq_entry.grid(row=7,column=2)


  def get_entry(self):
    """
    Returns the dict representing a channel
    """
    d = {}
    d['lbl'] = self.t_lbl.get()
    assert d['lbl'],"Cannot use an empty label"
    assert not d['lbl'] in [i['lbl'] for i in self.chan_list],\
        "Label already in use!"
    d['name'] = self.t_chan.get()
    try:
      d['name'] = int(d['name'])
    except ValueError:
      assert d['name'], "Cannot use an empty chan"
    assert not d['name'] in [i['name'] for i in self.chan_list],\
        "Channel already in use!"
    if not self.t_range.get():
      self.t_range.insert(0,'10')
    d['range'] = float(self.t_range.get())
    if not self.t_gain.get():
      self.t_gain.insert(0,'1')
    d['gain'] = float(self.t_gain.get())
    if not self.t_offset.get():
      self.t_offset.insert(0,'0')
    d['offset'] = float(self.t_offset.get())
    d['make_zero'] = bool(self.c_zero_var.get())
    return d

  def add_chan(self,event=None):
    try:
      self.chan_list.append(self.get_entry())
    except (AssertionError,ValueError) as e:
      self.out(e)
      return
    c = self.chan_list[-1]
    self.listbox.insert(tk.END,c['lbl']+": "+str(c['name']))

  def del_chan(self,event=None):
    try:
      i = self.listbox.curselection()[0]
    except IndexError:
      self.out("Please select an entry first")
    del self.chan_list[i]
    self.listbox.delete(tk.ANCHOR)

  def edit_chan(self,event=None):
    try:
      d = self.chan_list[self.listbox.curselection()[0]]
    except IndexError:
      self.out("Please select an entry first")
      return
    replace = lambda f,s: (f.delete(0,tk.END),f.insert(0,str(s)))
    replace(self.t_lbl,d['lbl'])
    replace(self.t_chan,d['name'])
    replace(self.t_range,d['range'])
    replace(self.t_gain,d['gain'])
    replace(self.t_offset,d['offset'])
    if d['make_zero']:
      self.c_zero.select()
    else:
      self.c_zero.deselect()
    self.del_chan()

  def get_config(self):
    return float(self.freq_entry.get()),self.chan_list

  def set_config(self,config):
    freq,self.chan_list = config
    self.listbox.delete(0,tk.END)
    for c in self.chan_list:
      self.listbox.insert(tk.END,c['lbl']+": "+str(c['name']))
    self.freq_entry.delete(0,tk.END)
    self.freq_entry.insert(0,str(freq))
