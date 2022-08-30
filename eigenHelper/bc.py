from bokeh.models import Div, RadioButtonGroup, NumericInput, Button
from utils import *

def activateSupportImg(choice):
    padding = ['&emsp;', '&emsp;', '&emsp; &nbsp', '&emsp;', '&emsp;', '&emsp;']
    newText = '&nbsp &nbsp'
    for i in range(6):
        if i == choice:
            newText += f'<img src="/eigenHelper/static/support{i}.png"> {padding[i]}'
        else:
            newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def deactivateSupportImg():
    padding = ['&emsp;', '&emsp;', '&emsp; &nbsp', '&emsp;', '&emsp;', '&emsp;']
    newText = '&nbsp &nbsp'
    for i in range(6):
        newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def activateBCModule(bcdict):
    for _, val in bcdict.items():
        val.disabled = False
    bcdict['rbgDiv'].text = activateSupportImg(0)

def deactivateBCModule(bcdict):
    for _, val in bcdict.items():
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

    rbg = RadioButtonGroup(labels=['S1', 'S2', 'S3', 'S4', 'S5', 'S6'], active=0, disabled=True)
    addToNodeWidget = NumericInput(value=0, title="Add support at node:",mode='int', width=50,height=50, disabled=True)
    addSupportButton = Button(label="Add Support", button_type="primary", width=50, disabled=True)
    deleteFromNodeWidget = NumericInput(value=0, title="Remove support at node:",mode='int', width=50,height=50, disabled=True)
    deleteSupportButton = Button(label="Remove Support", button_type="warning", width=50, disabled=True)
    deleteAllSupportsButton = Button(label="Remove All Supports", button_type="danger", width=50, disabled=True)
    rbgText = deactivateSupportImg()
    rbgDiv = Div(text=rbgText, width=400, height=50)
    bcLayoutDict = {'rbg':rbg, 'addToNodeWidget':addToNodeWidget, 'addSupportButton':addSupportButton, \
        'deleteFromNodeWidget':deleteFromNodeWidget, 'deleteSupportButton':deleteSupportButton, \
        'deleteAllSupportsButton':deleteAllSupportsButton, 'rbgDiv':rbgDiv}
    return bcLayoutDict