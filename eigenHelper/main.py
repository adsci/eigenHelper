from bokeh.io import curdoc
from bokeh.models import Div, NumericInput, Button, ColumnDataSource, LabelSet, CustomJS
from bokeh.layouts import column, row, Spacer
from bokeh.plotting import figure
from functools import partial
from utils import *

def modify_doc(doc, debug=False):
    #Plot
    def makePlot(nsetCDS, elsetCDS):
        p = figure(width=800, height=800, match_aspect=True)
        ### NODES
        renderer = p.circle('x','y',source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
        labels = LabelSet(x='x', y='y', text='IDs',
              x_offset=5, y_offset=5, source=nsetCDS, render_mode='canvas')
        p.add_layout(labels)
        renderer.js_on_change('visible', CustomJS(args=dict(ls=labels), code="ls.visible = cb_obj.visible;"))
        ### ELEMENTS
        p.line('x','y', source=elsetCDS, line_width=5, color='black', legend_label="Elements")
        ### LEGEND
        p.legend.location = "top_left"
        p.legend.click_policy="hide"
        return p

    def updateCoordData(nodeset, nodeCDS):
        ex, ey, ids = nodeset.getExEy()
        nodeCDS.data = {'x':ex, 'y':ey, 'IDs':ids}

    def updateElementData(elemset, elemCDS):
        ex, ey = elemset.getExEy()
        elemCDS.data = {'x':ex, 'y':ey}

    """
    Node module
    """
    nset = NodeSet()
    nIDWidget = NumericInput(value=1, title="Node ID:",mode='int', width=50,height=50)
    nXWidget = NumericInput(value=0, title="x [m]:",mode='float', width=75,height=50)
    nYWidget = NumericInput(value=0, title="y [m]:",mode='float', width=75)
    delNodeNumWidget = NumericInput(value=0, title="Node to be deleted:",mode='int', width=50)
    addNodeButton = Button(label="Add Node", button_type="primary", width=50 )
    delNodeButton = Button(label="Delete Node", button_type="danger", width=50 )
    assignDOFsButton = Button(label="Assign DOFs", button_type="success", width=50 )

    divNodes = Div(text=nset.printInfo(debug), width=250, height=300)

    #node module callbacks
    def addNodeOnClick(nodeset, xCoordInput, yCoordInput, nidInput, dtext, nodeCDS):
        if nidInput.value <= 0:
            return
        added = nodeset.addNode(float(xCoordInput.value),float(yCoordInput.value),nidInput.value)
        if added:
            nidInput.value = nodeset.getNextID()
        updateCoordData(nodeset,nodeCDS)
        dtext.text=nodeset.printInfo(debug) + '<br><p style="color:red"><b>Assign DOFs when node input ready</b></p>'

    def delNodeOnClick(nodeset, delNodeInput, dtext, nodeCDS):
        if not nodeset.nodes or delNodeInput.value <= 0 or delNodeInput.value >= nodeset.getNextID():
            return
        nodeset.deleteNodeWithID(delNodeInput.value)
        delNodeInput.value = 0
        updateCoordData(nodeset, nodeCDS)
        dtext.text=nodeset.printInfo(debug) + '<br><p style="color:red"><b>Assign DOFs when node input ready</b></p>'

    def assignDOFsOnClick(nodeset, dtext):
        if nodeset.nodes:
            nodeset.assignDOFs()
            dtext.text=nodeset.printInfo(debug) + '<br><p style="color:green"><b>DOFs assigned, ready for element input</b></p>'

    """
    Element module
    """
    eset = ElementSet()
    eIDWidget = NumericInput(value=1, title="Element ID:",mode='int', width=50,height=50)
    enaWidget = NumericInput(value=0, title="Node A:",mode='int', width=50,height=50)
    enbWidget = NumericInput(value=0, title="Node B:",mode='int', width=50)
    eYoungWidget = NumericInput(value=1, title="E [Pa]",mode='int', width=100,height=50)
    eDensityWidget = NumericInput(value=1, title="rho [kg/m^3]:",mode='int', width=100,height=50)
    eAreaWidget = NumericInput(value=1, title="A [m^2]:",mode='int', width=100,height=50)
    eInertiaWidget = NumericInput(value=1, title="I [m^4]:",mode='int', width=100,height=50)
    delElNumWidget = NumericInput(value=0, title="Element to be deleted:",mode='int', width=50)
    addElemButton = Button(label="Add Element", button_type="primary", width=100 )
    delElemButton = Button(label="Delete Element", button_type="danger", width=120 )

    divElements = Div(text=eset.printInfo(debug), width=350, height=300)

    #element module callbacks
    def addElemOnClick(nodeset, elemset, eidWidget, naWidget, nbWidget, youngWidget, densityWidget, areaWidget, inertiaWidget, dtext, elemCDS):
        if eidWidget.value <= 0:
            return
        added = elemset.addElement(eidWidget.value, nodeset.getNodeWithID(naWidget.value), nodeset.getNodeWithID(nbWidget.value), \
            {'E':youngWidget.value, 'rho':densityWidget.value, 'A':areaWidget.value, 'I':inertiaWidget.value}) 
        if added:
            eidWidget.value = elemset.getNextID()
        updateElementData(elemset,elemCDS)
        dtext.text=elemset.printInfo(debug)

    def delElemOnClick(elemset, delElWidget, dtext, elemCDS):
        if not elemset.elements or delElWidget.value <= 0 or delElWidget.value >= elemset.getNextID():
            return
        elemset.deleteElemWithID(delElWidget.value)
        delElWidget.value = 0
        updateElementData(elemset, elemCDS)
        dtext.text=elemset.printInfo(debug)


    """
    Plot
    """
    exNodes, eyNodes, idlist = nset.getExEy()
    ncds = ColumnDataSource({'x':exNodes, 'y':eyNodes, 'IDs':idlist})
    exElems, eyElems = eset.getExEy()
    ecds = ColumnDataSource({'x':exElems, 'y':eyElems})
    p = makePlot(ncds, ecds)

    """
    Handlers
    """
    addNodeButton.on_click(partial(addNodeOnClick, nodeset=nset, xCoordInput=nXWidget, yCoordInput=nYWidget,\
         nidInput=nIDWidget, dtext=divNodes, nodeCDS=ncds))
    delNodeButton.on_click(partial(delNodeOnClick, nodeset=nset, delNodeInput=delNodeNumWidget, dtext=divNodes, nodeCDS=ncds))
    assignDOFsButton.on_click(partial(assignDOFsOnClick, nodeset=nset, dtext=divNodes))

    addElemButton.on_click(partial(addElemOnClick, nodeset=nset, elemset=eset, eidWidget=eIDWidget,\
        naWidget=enaWidget, nbWidget=enbWidget, youngWidget=eYoungWidget, densityWidget=eDensityWidget,\
        areaWidget=eAreaWidget, inertiaWidget=eInertiaWidget, dtext=divElements, elemCDS=ecds))
    delElemButton.on_click(partial(delElemOnClick, elemset=eset, delElWidget=delElNumWidget, dtext=divElements, elemCDS=ecds))

    """
    Layout
    """
    nodeLayout = row(column(nIDWidget, nXWidget, nYWidget, addNodeButton), \
        column(Spacer(width=100,height=17), assignDOFsButton, Spacer(width=100,height=nXWidget.height+10), \
            delNodeNumWidget, delNodeButton), divNodes)
    elemLayout =  row(column(enaWidget, eYoungWidget, eAreaWidget, addElemButton), \
                    column(enbWidget, eDensityWidget, eInertiaWidget), \
                    column(eIDWidget, Spacer(width=100,height=eIDWidget.height+10), delElNumWidget, delElemButton) , divElements)

    layout = row(column(nodeLayout, elemLayout), p)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc(),debug=True)
