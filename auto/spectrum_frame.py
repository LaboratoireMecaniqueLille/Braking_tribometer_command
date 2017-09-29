#coding: utf-8

import Tkinter as tk

class SpectrumFrame(tk.Frame):
  """
  This widget will create the frame to configure the Spectrum inputs

  It has 2 main sections:
    - Multiple input fields on the left, to type the settings of a new channel
    - The list of the channels that were already created
  The arrow buttons in between allow to add a channel to the list or remove it
  and write its settings to the field to edit them.
  You CANNOT have two channels with the same name or a channel with the same
  name as one from the Labjack Frame.
  Channels must be ints (0 to 15), corresponding to the channel on the card.

  The label can be any unique string as long as there are no conflicts. It will
  be used to identify it in the graphs, and will be saved in the hdf5 file.

  The gain is simply saved as a metadata in the hdf5 file but it will NOT be
  applied to the stream and it is YOUR job to convert the DL value to the
  physical value. For simplicity, the table root.factors in the hdf5 file
  holds the values to multiply your DL by to get the physical value
  (assuming a gain in unit/V).
  """
  def __init__(self,root):
    tk.Frame.__init__(self,root,borderwidth=2,relief=tk.GROOVE)
    self.name = "spectrum"
    self.root = root
    self.title = tk.Label(self,text=self.name.capitalize(),
        font=("Helvetica",20))
    self.title.grid(row=0,column=0,columnspan=10)
    self.out = self.root.output
    self.listbox = tk.Listbox(self)
    self.listbox.grid(row=1,column=3,rowspan=3,columnspan=2)
    self.edit_button = tk.Button(self,text="<-",command=self.edit_chan)
    self.edit_button.grid(row=3,column=2)
    self.add_button = tk.Button(self,text="->",command=self.add_chan)
    self.add_button.grid(row=2,column=2)
    self.del_button = tk.Button(self,text="Delete",command=self.del_chan)
    self.del_button.grid(row=4,column=4)
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

    tk.Label(self,text="Frequency (kHz)").grid(row=7,column=1)
    self.freq_entry = tk.Entry(self)
    self.freq_entry.insert(0,"100")
    self.freq_entry.grid(row=7,column=2)

  def get_entry(self):
    d = {}
    d['lbl'] = self.t_lbl.get()
    assert d['lbl'],"Cannot use an empty label"
    assert not d['lbl'] in [i['lbl'] for i in self.chan_list],\
        "Label already in use!"
    d['chan'] = self.t_chan.get()
    try:
      d['chan'] = int(d['chan'])
    except ValueError:
      self.out("Please use integer values for Spectrum channels")
      return
    assert not d['chan'] in [i['chan'] for i in self.chan_list],\
        "Channel already in use!"
    if not self.t_range.get():
      self.t_range.insert(0,'10')
    d['range'] = float(self.t_range.get())
    if not self.t_gain.get():
      self.t_gain.insert(0,'1')
    d['gain'] = float(self.t_gain.get())
    return d

  def add_chan(self,event=None):
    try:
      self.chan_list.append(self.get_entry())
    except (AssertionError,ValueError) as e:
      self.out(e)
      return
    c = self.chan_list[-1]
    self.listbox.insert(tk.END,c['lbl']+": "+str(c['chan']))

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
    replace(self.t_chan,d['chan'])
    replace(self.t_range,d['range'])
    replace(self.t_gain,d['gain'])
    self.del_chan()

  def get_config(self):
    return float(self.freq_entry.get()),self.chan_list

  def set_config(self,config):
    freq,self.chan_list = config
    self.listbox.delete(0,tk.END)
    for c in self.chan_list:
      self.listbox.insert(tk.END,c['lbl']+": "+str(c['chan']))
    self.freq_entry.delete(0,tk.END)
    self.freq_entry.insert(0,str(freq))
