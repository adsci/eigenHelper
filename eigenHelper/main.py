from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from functools import partial
from utils import *
from node import *
from element import *
from bc import *
from plot import *


def modify_doc(doc, debug=False):

    #Create Node module
    ndic = createNodeLayout(debug)

    #Create Element module
    edic = createElementLayout(debug)

    #Create Boundary Conditions module
    bcdic = createBCLayout(debug)

    #Create Plot module
    p, ncds, ecds, scds = createPlotLayout(ndic['nset'], edic['eset'], bcdic['sset'])

    """
    Handlers
    """
    ndic['addNodeButton'].on_click(partial(addNodeOnClick, nModule=ndic, nodeCDS=ncds, debugInfo=debug))
    ndic['delNodeButton'].on_click(partial(delNodeOnClick, nModule=ndic, elModule=edic, nodeCDS=ncds, debugInfo=debug))
    ndic['delAllNodesButton'].on_click(partial(delAllNodesOnClick, nModule=ndic, elModule=edic, nodeCDS=ncds, debugInfo=debug))
    ndic['assignDOFsButton'].on_click(partial(assignDOFsOnClick, nModule=ndic, elModule=edic, debugInfo=debug))

    edic['addElemButton'].on_click(partial(addElemOnClick, nModule=ndic, elModule=edic, elemCDS=ecds, debugInfo=debug))
    edic['delElemButton'].on_click(partial(delElemOnClick, elModule=edic, bcModule=bcdic, elemCDS=ecds, debugInfo=debug))
    edic['delAllElemButton'].on_click(partial(delAllElemOnClick, elModule=edic, bcModule=bcdic, elemCDS=ecds, debugInfo=debug))
    edic['assembleButton'].on_click(partial(assembleOnClick, elModule=edic, bcModule=bcdic, debugInfo=debug))

    bcdic['rbg'].on_click(partial(changeActiveBC, bcModule=bcdic))
    bcdic['addSupportButton'].on_click(partial(addSupportOnClick, nModule=ndic, bcModule=bcdic, ssetCDS=scds, debugInfo=debug))
    bcdic['deleteSupportButton'].on_click(partial(delSupportOnClick, bcModule=bcdic, ssetCDS=scds, debugInfo=debug))
    bcdic['deleteAllSupportsButton'].on_click(partial(delAllSupportsOnClick, bcModule=bcdic, ssetCDS=scds, debugInfo=debug))

    """
    Layout
    """
    nodeLayout = row(column(ndic['nIDWidget'], ndic['nXWidget'], ndic['nYWidget'], ndic['addNodeButton']), \
        column(Spacer(width=100,height=17), ndic['assignDOFsButton'], Spacer(width=100,height=ndic['nXWidget'].height+10), \
            ndic['delNodeNumWidget'], ndic['delNodeButton'], ndic['delAllNodesButton']), Spacer(width=25), ndic['divNodes'])
    elemLayout =  row(column(edic['enaWidget'], edic['eYoungWidget'], edic['eAreaWidget'], edic['addElemButton']), \
                    column(edic['enbWidget'], edic['eDensityWidget'], edic['eInertiaWidget']), \
                    column(edic['eIDWidget'], Spacer(width=100,height=17), edic['assembleButton'], edic['delElNumWidget'], \
                         edic['delElemButton'], edic['delAllElemButton']), \
                             Spacer(width=75), edic['divElements'])
    bcLayout = row(column(bcdic['rbg'], bcdic['rbgDiv'], row(column(bcdic['addToNodeWidget'], bcdic['addSupportButton']), Spacer(width=150),\
        column(bcdic['deleteFromNodeWidget'], bcdic['deleteSupportButton'], bcdic['deleteAllSupportsButton']) )), \
        Spacer(width=20), bcdic['divSupports'])

    layout = row(column(nodeLayout, elemLayout, bcLayout), p)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc(),debug=True)
