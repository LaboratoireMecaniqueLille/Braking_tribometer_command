#coding: utf-8

# The background image
img = "/home/tribo/Code/crappy/data/Pad.png"
# The points and their labels
points = [
    ("T1", (185,430)),
    #("T2",(145, 320)),
    ("T3",(105, 220)),  
    #("T4",(720, 370)), 
    #("T5",(720, 250)), 
    #("T6",(720, 125)), 
    #("T7",(1220, 410)), 
    #("T8",(1260, 320)), 
    #("T9",(1300, 230)), 
]

trange = [20,300] # Temperature scale

options = [{'type':'dot_text',
            'coord':pos,
            'text':l+' = %.1f',
            'label':l} for l,pos in points]

def get_drawing():
  #from crappy.blocks import Drawing
  from crappy import blocks
  return blocks.Drawing(img,options, crange=[20,300], title="Temperatures",backend="qt4agg")
