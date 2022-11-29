from bokeh.models import Div, Toggle
from utils import *


def createHowToContent():
    introduction = "How to use this app:"
    nodeinfo = '''
    1. Define model nodes. For each node, enter its coordinates and click "Add Node". When ready, click "Go to Define Elements" button.
    '''
    eleminfo = '''
    2. Define elements. For each element, define its starting and ending node, as well as its material and geometrical properties.
    Hinges can be defined by checking the appropriate box. When ready, click "Go to Define Supports" button.
    '''
    supportinfo = '''
    3. Define supports by specifying the support type and the node at which the support is to be added.
    '''
    checkinfo = '''
    4. Click "Check Model" button. If the model is defined correctly, "Solve" button will appear. Otherwise, resolve the possible issues.
    '''
    solveinfo = '''
    5. Solve the eigenvalue problem by clicking the "Solve" button.
    '''
    howtocontent = [introduction, nodeinfo, eleminfo, supportinfo, checkinfo, solveinfo]
    colors = ['black'] + 5*['red']
    return howtocontent, colors

def makeTitle():
    title = '<h1 style="font-family: helvetica; font-size:40pt; font-style:bold; display:inline"><em>eigenHelper</em></h1>' + \
            '<p>Copyright (c) 2022 Adam Sciegaj</p> ' + \
            '<a href="https://github.com/adsci/eigenHelper/blob/main/README.md">Full README</a>'
    return title

def converttohtml(text, bold, colors):
    html = ''
    for i, line in enumerate(text):
        html += f'''<p style="color:{colors[i]}">{text[i]}</p>'''

    return '<b>'+html+'</b>' if bold else html

def updateHowtoDiv(htModule):
    htModule['divHowto'].text = makeTitle() + converttohtml(htModule['howtotext'], True, htModule['colors'])

"""
Node module callbacks
"""
def toggleHelp(attr, old, new, htModule):
    show(htModule['divHowto']) if new else hide(htModule['divHowto'])

"""
HowTo module layout
"""
def createHowToLayout():
    howtotext, colors = createHowToContent()
    titletext = makeTitle()
    divHowto =  Div(text= titletext + converttohtml(howtotext,True,colors), width=1000, height=350, visible=False)
    showHelpToggle = Toggle(label="Show/Hide Help", \
        button_type='default', width=50, height=50)

    howtoDict = {'divHowto':divHowto, 'showHelpToggle':showHelpToggle, 'colors':colors, 'howtotext':howtotext}
    return howtoDict