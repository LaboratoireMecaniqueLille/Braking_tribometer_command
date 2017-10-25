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


def check_chan(chan):
  """
  To make sure we follow the rules for channel opening (see sepctrum doc)

  0,1,2,4 or 8 per module, same number of channel per module if both are used
  If this is not respected, open unused channels to comply
  Also, order the label correctly to comply with Spectrum multiplexing
  (Alternate on each module in numerical order)
  Ex: 0,2,9,10 are open, data will be 0,9,2,10,0,9,...
  """
  chan = sorted(chan)
  assert all([c in range(16) for c in chan]),\
      "All spectrum channels must be between and 15"
  num = len([c for c in chan if c < 8])
  chan = chan[:num],chan[num:]
  nchan = max(len(chan[0]),len(chan[1]))
  while nchan not in [1,2,4,8]:
    nchan += 1
  if len(chan[0]) not in (0,nchan) or len(chan[1]) not in (0,nchan):
    print("[Warning] Cannot open this combination of channels on Spectrum")
    print("  I will add useless channels for you")
  while 0 < len(chan[0]) < nchan:
    left = [i for i in range(8) if i not in chan[0]]
    chan[0].append(left[0])
  while 0 < len(chan[1]) < nchan:
    left = [i for i in range(8,16) if i not in chan[1]]
    chan[1].append(left[0])
  rchan = []
  chan = sorted(chan[0]),sorted(chan[1])
  if chan[0] and chan[1]:
    for c1,c2 in zip(*chan):
      rchan.extend([c1,c2])
  else:
    rchan = chan[0] or chan[1]
  print("DEBUG channel order:",rchan)
  return rchan
