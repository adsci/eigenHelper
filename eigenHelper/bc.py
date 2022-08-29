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


"""
Node module callbacks
"""
def changeActiveBC(newChoice, rbgDiv):
    rbgDiv.text = activateSupportImg(newChoice)

"""
Boundary Conditions module layout
"""
def createBCLayout(debug=False):

    rbg = RadioButtonGroup(labels=['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'], active=0, disabled=False)
    rbgText = '<img src="/eigenHelper/static/support0.png" style="opacity:0.4;filter:alpha(opacity=40);"> &nbsp' + \
        '<img src="/eigenHelper/static/support1.png" style="opacity:0.4;filter:alpha(opacity=40);"> &emsp;' + \
        '<img src="/eigenHelper/static/support2.png" style="opacity:0.4;filter:alpha(opacity=40);"> &nbsp' + \
        '<img src="/eigenHelper/static/support3.png" style="opacity:0.4;filter:alpha(opacity=40);"> &nbsp' + \
        '<img src="/eigenHelper/static/support4.png" style="opacity:0.4;filter:alpha(opacity=40);"> &emsp;' + \
        '<img src="/eigenHelper/static/support5.png" style="opacity:0.4;filter:alpha(opacity=40);"> &emsp;' + \
        '<img src="/eigenHelper/static/support6.png" style="opacity:0.4;filter:alpha(opacity=40);"> &nbsp'
    rbgDiv = Div(text=rbgText, width=400)
    bcLayoutDict = {'rbg':rbg, 'rbgDiv':rbgDiv}
    return bcLayoutDict