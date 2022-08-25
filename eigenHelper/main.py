from bokeh.io import curdoc
from bokeh.models import Div, NumericInput, Button, ColumnDataSource, LabelSet, CustomJS
from bokeh.layouts import column, row, Spacer
from bokeh.plotting import figure
from functools import partial
from utils import *

def modify_doc(doc):
    #Plot
    def makePlot(nsetCDS):
        p = figure(width=800, height=800)
        renderer = p.circle('x','y',source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
        labels = LabelSet(x='x', y='y', text='IDs',
              x_offset=5, y_offset=5, source=nsetCDS, render_mode='canvas')
        p.add_layout(labels)
        renderer.js_on_change('visible', CustomJS(args=dict(ls=labels), code="ls.visible = cb_obj.visible;"))
        p.legend.location = "top_left"
        p.legend.click_policy="hide"
        return p

    def updateCoordData(nodeset, nodeCDS):
        ex, ey, ids = nodeset.getExEy()
        nodeCDS.data = {'x':ex, 'y':ey, 'IDs':ids}

    """
    Node module
    """
    nset = NodeSet()
    nID = NumericInput(value=1, title="Node ID:",mode='int', width=75,height=50)
    nX = NumericInput(value=0, title="Enter x coordinate:",mode='float', width=75,height=50)
    nY = NumericInput(value=0, title="Enter y coordinate:",mode='float', width=75)
    delNodeNum = NumericInput(value=0, title="Node to be deleted:",mode='int', width=75)
    addNodeButton = Button(label="Add Node", button_type="primary", width=120 )
    delNodeButton = Button(label="Delete Node", button_type="danger", width=120 )

    div = Div(text=nset.__str__(), width=150, height=300)

    #node module callbacks
    def addNodeOnClick(nodeset, xCoordInput, yCoordInput, nidInput, dtext, nodeCDS):
        if nidInput.value <= 0:
            return
        added = nodeset.addNode(float(xCoordInput.value),float(yCoordInput.value),nidInput.value)
        if added:
            nidInput.value = nodeset.getNextID()
        updateCoordData(nodeset,nodeCDS)
        dtext.text=nodeset.__str__()

    def delNodeOnClick(nodeset, delNodeInput, dtext, nodeCDS):
        if not nodeset.nodes or delNodeInput.value <= 0 or delNodeInput.value >= nodeset.getNextID():
            return
        nodeset.deleteNodeWithID(delNodeInput.value)
        delNodeInput.value = 0
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
    addNodeButton.on_click(partial(addNodeOnClick, nodeset=nset, xCoordInput=nX, yCoordInput=nY, nidInput=nID, dtext=div, nodeCDS=ncds))
    delNodeButton.on_click(partial(delNodeOnClick, nodeset=nset, delNodeInput=delNodeNum, dtext=div, nodeCDS=ncds))

    """
    Layout
    """
    layout = row(column(nID, nX, nY, addNodeButton), column(Spacer(width=100,height=nX.height+10), \
        Spacer(width=100,height=nX.height+10), delNodeNum, delNodeButton), div, p)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc())
