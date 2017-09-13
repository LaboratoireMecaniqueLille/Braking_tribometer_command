#coding: utf-8

import Tkinter as tk

class GraphFrame(tk.Frame):
  def __init__(self,root,labels_getter,graphs={}):
    self.get_labels = labels_getter
    self.out = root.output
    tk.Frame.__init__(self,root,borderwidth=2,relief=tk.GROOVE)
    self.graph_list = tk.Listbox(self,height=5,selectmode=tk.SINGLE)
    self.graph_list.grid(row=0,column=0,columnspan=2)
    self.graph_list.bind("<<ListboxSelect>>",self.select_graph)
    self.b_add = tk.Button(self,text="+",command=self.add_graph)
    self.b_add.grid(row=1,column=0)
    self.b_remove = tk.Button(self,text='-',command=self.del_graph)
    self.b_remove.grid(row=1,column=1)

    self.graph_label_list = tk.Listbox(self)
    self.graph_label_list.grid(row=0,column=2,rowspan=3)
    self.b_left = tk.Button(self,text='<-',command=self.label_to_graph)
    self.b_left.grid(row=0,column=3)
    self.b_right = tk.Button(self,text='->',command=self.graph_to_label)
    self.b_right.grid(row=1,column=3)
    self.label_list = tk.Listbox(self)
    self.label_list.grid(row=0,column=4,rowspan=3)

    self.labels = self.get_labels()
    self.graph_dict = {}
    self.curr_graph = None
    if graphs:
      self.set_config(graphs)

  def set_config(self,graphs):
    self.graph_list.delete(0,tk.END)
    for labels in self.graph_dict.values():
      for l in labels:
        assert l in self.labels,"This label is not defined: "+l
    self.graph_dict = graphs
    for g in self.graph_dict:
      self.graph_list.insert(tk.END,g)

  ## CALLBACKS
  def select_graph(self,event=None):
    try:
      self.curr_graph = self.graph_list.get(self.graph_list.curselection()[0])
    except IndexError:
      self.curr_graph = None
    self.update_lists()

  def add_graph(self):
    i = 1
    while "Graph%d"%i in self.graph_dict:
      i+=1
    s = "Graph%d"%i
    self.graph_dict[s] = []
    self.graph_list.insert(tk.END,s)
    return s

  def del_graph(self):
    try:
      g_name = self.graph_list.get(self.graph_list.curselection()[0])
    except IndexError:
      self.out("Please select a graph first")
      return
    del self.graph_dict[g_name]
    self.graph_list.delete(tk.ANCHOR)

  def label_to_graph(self):
    try:
      lbl = self.label_list.get(self.label_list.curselection()[0])
    except IndexError:
      self.out("Please select a label first")
      return
    self.graph_dict[self.curr_graph].append(lbl)
    self.update_lists()

  def graph_to_label(self):
    try:
      lbl = self.graph_label_list.get(self.graph_label_list.curselection()[0])
    except IndexError:
      self.out("Please select a label first")
      return
    self.graph_dict[self.curr_graph].remove(lbl)
    self.update_lists()

# OTHER METHODS
  def update_lists(self):
    """
    Updates the two listboxes on the right
    """
    new_labels = self.get_labels()
    # Remove the labels that are not defined anymore
    for g in self.graph_dict:
      self.graph_dict[g] = filter(lambda x:x in new_labels,self.graph_dict[g])

    if self.curr_graph is None:
      self.label_list.delete(0,tk.END)
      self.graph_label_list.delete(0,tk.END)
      return
    self.graph_label_list.delete(0,tk.END)
    for l in self.graph_dict[self.curr_graph]:
      self.graph_label_list.insert(tk.END,l)
    self.label_list.delete(0,tk.END)
    for l in new_labels:
      if l not in self.graph_dict[self.curr_graph]:
        self.label_list.insert(tk.END,l)
