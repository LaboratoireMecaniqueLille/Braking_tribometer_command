#coding: utf-8
from __future__ import print_function,division

class HFSplit:
  def __init__(self,labels,index,gains,ranges):
    self.labels = labels
    self.index = index
    self.gains = [r*g/32000000 for g,r in zip(
      [gains[k] for k in sorted(gains.keys())],ranges)]

  def evaluate(self,data):
    r = {}
    r['t(s)'] = data['t(s)'][0]
    for l,i,g in zip(self.labels,self.index,self.gains):
      r[l] = g*data['stream'][0,i]
    return r


def check_chan(chan,labels,ranges,gains):
  """
  To make sure we follow the rules for channel opening (see sepctrum doc)
  0,1,2,4 or 8 per module, same number of channel per module if both are used
  If this is not respected, open unused channels to comply
  """
  chan,labels,ranges = [list(t) for t in zip(*sorted(zip(chan,labels,ranges)))]
  assert all([c in range(16) for c in chan]),\
      "All spectrum channels must be between and 15"
  num = len([c for c in chan if c < 8])
  chan = chan[:num],chan[num:]
  labels = labels[:num],labels[num:]
  ranges = ranges[:num],ranges[num:]
  nchan = max(len(chan[0]),len(chan[1]))
  while nchan not in [1,2,4,8]:
    nchan += 1
  if len(chan[0]) not in (0,nchan) or len(chan[1]) not in (0,nchan):
    print("[Warning] Cannot open this combination of channels on Spectrum")
    print("  I will add useless channels for you")
  while 0 < len(chan[0]) < nchan:
    left = [i for i in range(8) if i not in chan[0]]
    chan[0].append(left[0])
    labels[0].append('UNUSED%d'%left[0])
    ranges[0].append(10000)
    gains[left[0]] = 1
  while 0 < len(chan[1]) < nchan:
    left = [i for i in range(8,16) if i not in chan[1]]
    chan[1].append(left[0])
    labels[1].append('UNUSED%d'%left[0])
    ranges[0].append(10000)
    gains[left[1]] = 1
  return zip(*sorted(zip(sum(chan,[]),sum(labels,[]),sum(ranges,[]))))+[gains]
