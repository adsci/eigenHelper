from bokeh.io import curdoc
from bokeh.models import Div, NumericInput, Button, ColumnDataSource, LabelSet
from bokeh.layouts import column, row, Spacer
from bokeh.plotting import figure
from functools import partial
from utils import *

def modify_doc(doc):
    #Plot
    def makePlot(nsetCDS):
        p = figure(width=800, height=800)
        p.circle('x','y',source=nsetCDS, size=7, color="navy", alpha=0.5)
        labels = LabelSet(x='x', y='y', text='IDs',
              x_offset=5, y_offset=5, source=nsetCDS, render_mode='canvas')
        p.add_layout(labels)
        return p

    def updateCoordData(nodeset, nodeCDS):
        ex, ey, ids = nodeset.getExEy()
        nodeCDS.data = {'x':ex, 'y':ey, 'IDs':ids}

    """
    Node module
    """
    nset = NodeSet()
    nX = NumericInput(value=0, title="Enter x coordinate:",mode='float', width=75,height=50)
    nY = NumericInput(value=0, title="Enter y coordinate:",mode='float', width=75)
    delNodeNum = NumericInput(value=0, title="Node to be deleted:",mode='int', width=75)
    addNodeButton = Button(label="Add Node", button_type="primary", width=120 )
    delNodeButton = Button(label="Delete Node", button_type="danger", width=120 )

    div = Div(text=nset.__str__(), width=150, height=300)

    #node module callbacks
    def addNodeOnClick(nodeset, xCoordInput, yCoordInput, dtext, nodeCDS):
        nodeset.addNode(float(xCoordInput.value),float(yCoordInput.value))
        updateCoordData(nodeset,nodeCDS)
        dtext.text=nodeset.__str__()

    def delNodeOnClick(nodeset, delNodeInput, dtext, nodeCDS):
        if delNodeInput.value <= 0 or delNodeInput.value > nodeset.getNumberOfNodes():
            return
        nodeset.deleteNodeWithID(delNodeInput.value)
        updateCoordData(nodeset, nodeCDS)
        dtext.text=nodeset.__str__()

    """
    Plot
    """
    ex, ey, idlist = nset.getExEy()
    ncds = ColumnDataSource({'x':ex,'y':ey, 'IDs':idlist})
    p = makePlot(ncds)

    """
    Handlers
    """
    addNodeButton.on_click(partial(addNodeOnClick, nodeset=nset, xCoordInput=nX, yCoordInput=nY, dtext=div, nodeCDS=ncds))
    delNodeButton.on_click(partial(delNodeOnClick, nodeset=nset, delNodeInput=delNodeNum, dtext=div, nodeCDS=ncds))

    """
    Layout
    """
    layout = row(column(nX,nY, addNodeButton), column(Spacer(width=100,height=nX.height+10), delNodeNum, delNodeButton), div, p)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc())
