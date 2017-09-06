#coding: utf-8

# =======================================
# = The main interface of the auto mode =
# =======================================

from __future__ import print_function

import Tkinter as tk
from path_frame import PathFrame
from funcs import avail

root = tk.Tk()

path_frame = PathFrame(root,avail)

path_frame.grid(row=0,column=0)


"""
## test
p2 = PathFrame(root)
p3 = PathFrame(root)
p4 = PathFrame(root)

p2.grid(row=1,column=0)
p3.grid(row=0,column=1)
p4.grid(row=1,column=1)


##"""


root.mainloop()
