#coding:utf-8
from __future__ import print_function,division

from launch import launch

import pickle

with open("test.p","rb") as f:
  d = pickle.load(f)

launch(*d)
