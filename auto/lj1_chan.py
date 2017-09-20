#coding: utf-8
from __future__ import division

"""
This file defines all the channels that will be opened on the
master labjack
You can add channels, but remember that this Labjack drives all the
tribometer, so if possible use the second one meant for acquisition
"""
# The key of the dict will be used as the label for the Crappy prorgam

identifier = "470012972" # Serial number or name of the Labjack to open

in_chan = {
    'lj1_F(N)':{'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110},
    'lj1_rpm(t/min)':{'name':'AIN1','gain':413,'make_zero':False},
    'lj1_C(Nm)':{'name':'AIN2','gain':-50,'make_zero':True},
    }

out_chan = {
    'lj1_speed_cmd':{'name':'TDAC0','gain':1/412,'make_zero':False},
    'lj1_h2':{'name':'FIO2','direction':True},
    'lj1_h3':{'name':'FIO3','direction':True},
    'lj1_fcmd':{'name':46000,'direction':True},
    'lj1_fmode':{'name':46002,'direction':True},
    }
