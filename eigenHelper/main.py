from bokeh.io import curdoc
from bokeh.models import Div, NumericInput, Button
from bokeh.layouts import column, row, Spacer
from functools import partial
from utils import *

def modify_doc(doc):
    def addNodeOnClick(nodeset, xCoordInput, yCoordInput, dtext):
        nodeset.addNode(float(xCoordInput.value),float(yCoordInput.value))
        dtext.text=nodeset.__str__()

    def delNodeOnClick(nodeset, delNodeInput, dtext):
        if delNodeInput.value <= 0 or delNodeInput.value > nodeset.getNumberOfNodes():
            return
        nodeset.deleteNodeWithID(delNodeInput.value)
        dtext.text=nodeset.__str__()

    nset = NodeSet()
    nX = NumericInput(value=0, title="Enter x coordinate:",mode='float', width=75,height=50)
    nY = NumericInput(value=0, title="Enter y coordinate:",mode='float', width=75)
    delNodeNum = NumericInput(value=0, title="Node to be deleted:",mode='int', width=75)
    addNodeButton = Button(label="Add Node", button_type="primary", width=120 )
    delNodeButton = Button(label="Delete Node", button_type="danger", width=120 )
    div = Div(text=nset.__str__(), width=150, height=300)

    #handlers
    addNodeButton.on_click(partial(addNodeOnClick, nodeset=nset, xCoordInput=nX, yCoordInput=nY, dtext=div))
    delNodeButton.on_click(partial(delNodeOnClick, nodeset=nset, delNodeInput=delNodeNum, dtext=div))

    layout = row(column(nX,nY, addNodeButton), column(Spacer(width=100,height=nX.height+10), delNodeNum, delNodeButton), div)
    doc.add_root(layout)

modify_doc(curdoc())
