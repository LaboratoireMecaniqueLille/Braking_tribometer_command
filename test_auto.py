#coding: utf-8
from __future__ import print_function,division
from time import sleep

import crappy

def condition_pid(data):
  if data['f_cmd']:
    data['pid'] = 1
  else:
    data['pid'] = 0
  return data

path = [
    {'force':500,'speed':800,'duration':5},
    {'force':300,'speed':900,'duration':10},
    {'force':400,'speed':1000,'duration':8}
    ]


t = .2
tempo = "delay="+str(t)
tempo2 = "delay="+str(2*t)

hydrau_path_fio2 = [
    {'type':'constant','value':1,'condition':'hydrau<1'}, #Sorti, jusqu'à 0
    {'type':'constant','value':1,'condition':tempo}, # Attendre avant de rentrer
    {'type':'constant','value':0,'condition':tempo}, # Rentrer, attendre la fin
    {'type':'constant','value':0,'condition':'hydrau>0'}, # Avant de recommencer
    ]

hydrau_path_fio3 = [
    {'type':'constant','value':0,'condition':'hydrau<1'}, # Ouvert
    {'type':'constant','value':1,'condition':tempo2}, # fermer jusqu'à 2tempo
    {'type':'constant','value':0,'condition':'hydrau>0'}, # refermer
    {'type':'constant','value':1,'condition':tempo}, # fermer jusqu'à tempo
    ]

gen_fio2 = crappy.blocks.Generator(hydrau_path_fio2,repeat=True,cmd_label='h2')
gen_fio3 = crappy.blocks.Generator(hydrau_path_fio3,repeat=True,cmd_label='h3')

state_path = []
motor_path = []
pad_path = []
hydrau_path = []
for i,p in enumerate(path):
  state_path.extend(
    [ #Acceleration
      {'type':'constant','value':i,'condition':'rpm(t/m)>'+str(.99*p['speed'])},
      # Stabilisation
      {'type':'constant','value':i,'condition':'delay=3'},
      # Breaking
      {'type':'constant','value':i,'condition':'delay='+str(p['duration'])},
    ]
    )

  motor_path.extend(
      # new_cyle: trig_on_change de cycle (cycle=stage//3)
      [{'type':'constant','value':p['speed'],'condition':'stage>0'}]#*3
      )

  pad_path.extend(
      [{'type':'constant','value':p['force'],'condition':'stage>0'}]#*3
      )

  hydrau_path.extend(
      [
      {'type':'constant','value':1,'condition':'cycle>0'},
      {'type':'constant','value':1,'condition':'cycle>0'},
      {'type':'constant','value':0,'condition':'cycle>0'},
      ])

state_path.append({'type':'constant','value':-1,'condition':'delay=1'})
gen_state = crappy.blocks.Generator(state_path,cmd_label='stage')
gen_motor = crappy.blocks.Generator(motor_path,cmd_label='speed_cmd')
gen_pad = crappy.blocks.Generator(pad_path,cmd_label='f_cmd')
gen_hydrau = crappy.blocks.Generator(hydrau_path,cmd_label='hydrau',cmd=1)


crappy.link(gen_state,gen_motor,condition=crappy.condition.Trig_on_change('stage'))
crappy.link(gen_state,gen_pad,condition=crappy.condition.Trig_on_change('stage'))
crappy.link(gen_state,gen_hydrau,condition=crappy.condition.Trig_on_change('cycle'))


lj1 = crappy.blocks.IOBlock("Labjack_t7",identifier="470012972",channels=[
  {'name':'TDAC0','gain':1/412},
  {'name':'AIN0','gain':2061.3,'make_zero':False,'offset':110}, # Pad force
  {'name':'AIN1','gain':413,'make_zero':True}, # rpm
  {'name':'AIN2','gain':-50,'make_zero':True}, # torque
  {'name':'FIO2','direction':True}, # Hydrau
  {'name':'FIO3','direction':True}, # ..
  {'name':46000,'direction':True},
  {'name':46002,'direction':True},
  ],labels=['t(s)','F(N)','rpm(t/m)','C(Nm)'],cmd_labels=['speed_cmd','h2','h3','f_cmd','pid'])

crappy.link(lj1,gen_state)

crappy.link(gen_motor,lj1)
crappy.link(gen_pad,lj1,condition=condition_pid)
crappy.link(gen_hydrau,gen_fio2)
crappy.link(gen_hydrau,gen_fio3)
crappy.link(gen_fio2,lj1)
crappy.link(gen_fio3,lj1)


graph_speed = crappy.blocks.Grapher(('t(s)','rpm(t/m)'))
crappy.link(lj1,graph_speed)
graph_force = crappy.blocks.Grapher(('t(s)','F(N)'))
crappy.link(lj1,graph_force)
graph_torque = crappy.blocks.Grapher(('t(s)','C(Nm)'))
crappy.link(lj1,graph_torque)

status_reader = crappy.blocks.Reader("status")
crappy.link(gen_state,status_reader,condition=crappy.condition.Trig_on_change('cycle'))

servostar = crappy.actuator.Servostar('/dev/ttyS4')
servostar.open()


#servostar.set_mode_analog()
servostar.set_position(-1800)
sleep(1)
print("SERVOSTAR:",servostar.get_position())
servostar.set_position(-1800)
sleep(1)
print("SERVOSTAR:",servostar.get_position())

#crappy.start()
