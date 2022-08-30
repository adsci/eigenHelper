from bokeh.models import Div, RadioButtonGroup
from utils import *

def activateSupportImg(choice):
    padding = ['&nbsp', '&emsp;', '&nbsp', '&nbsp', '&emsp;', '&emsp;', '&nbsp']
    newText = ''
    for i in range(7):
        if i == choice:
            newText += f'<img src="/eigenHelper/static/support{i}.png"> {padding[i]}'
        else:
            newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def deactivateSupportImg():
    padding = ['&nbsp', '&emsp;', '&nbsp', '&nbsp', '&emsp;', '&emsp;', '&nbsp']
    newText = ''
    for i in range(7):
        newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def activateBCModule(bcdict):
    for key, val in bcdict.items():
        val.disabled = False
    bcdict['rbgDiv'].text = activateSupportImg(0)

def deactivateBCModule(bcdict):
    for key, val in bcdict.items():
        val.disabled = True
    bcdict['rbgDiv'].text = deactivateSupportImg()

"""
Node module callbacks
"""
def changeActiveBC(newChoice, bcModule):
    bcModule['rbgDiv'].text = activateSupportImg(newChoice)

"""
Boundary Conditions module layout
"""
def createBCLayout(debug=False):

    rbg = RadioButtonGroup(labels=['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'], active=0, disabled=True)
    rbgText = deactivateSupportImg()
    rbgDiv = Div(text=rbgText, width=400)
    bcLayoutDict = {'rbg':rbg, 'rbgDiv':rbgDiv}
    return bcLayoutDict