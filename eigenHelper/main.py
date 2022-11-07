from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from functools import partial
from utils import *
from node import *
from element import *
from bc import *
from plot import *
from solver import *


def modify_doc(doc, debug=False):

    #Create Node module
    ndic = createNodeLayout(debug)

    #Create Element module
    edic = createElementLayout(debug)

    #Create Boundary Conditions module
    bcdic = createBCLayout(debug)

    #Create Solver module
    soldic = createSolverLayout(debug)

    #Create Plot module
    p,  lsets, ncds, ecds, scds, mcds = createPlotLayout(ndic['nset'], edic['eset'], bcdic['sset'])

    """
    Handlers
    """
    ndic['addNodeButton'].on_click(partial(addNodeOnClick, nModule=ndic, solModule=soldic, nodeCDS=ncds, debugInfo=debug))
    ndic['delNodeButton'].on_click(partial(delNodeOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic,\
        nodeCDS=ncds, elemCDS=ecds, ssetCDS=scds, modeCDS=mcds, debugInfo=debug))
    ndic['delAllNodesButton'].on_click(partial(delAllNodesOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic,\
        nodeCDS=ncds, elemCDS=ecds, ssetCDS=scds, modeCDS=mcds, debugInfo=debug))
    ndic['assignDOFsButton'].on_click(partial(assignDOFsOnClick, nModule=ndic, elModule=edic, solModule=soldic, debugInfo=debug))
    ndic['nodeLabelsToggle'].on_change('active', partial(toggleNodeLabels, labels=lsets))
    ndic['showNodeInfoToggle'].on_change('active', partial(toggleNodeInfo, nModule=ndic))

    edic['addElemButton'].on_click(partial(addElemOnClick, nModule=ndic, elModule=edic, solModule=soldic, nodeCDS=ncds, elemCDS=ecds, debugInfo=debug))
    edic['delElemButton'].on_click(partial(delElemOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic, \
        nodeCDS=ncds, elemCDS=ecds, modeCDS=mcds, debugInfo=debug))
    edic['delAllElemButton'].on_click(partial(delAllElemOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic, \
        elemCDS=ecds, ssetCDS=scds, modeCDS=mcds, debugInfo=debug))
    edic['assembleButton'].on_click(partial(assembleOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic, \
        nodeCDS=ncds, debugInfo=debug))
    edic['elemLabelsToggle'].on_change('active', partial(toggleElementLabels, labels=lsets))
    edic['showElemInfoToggle'].on_change('active', partial(toggleElementInfo, elModule=edic))

    bcdic['rbg'].on_click(partial(changeActiveBC, bcModule=bcdic))
    bcdic['addSupportButton'].on_click(partial(addSupportOnClick, nModule=ndic, bcModule=bcdic, solModule=soldic, ssetCDS=scds, debugInfo=debug))
    bcdic['deleteSupportButton'].on_click(partial(delSupportOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic, \
        ssetCDS=scds, modeCDS=mcds, debugInfo=debug))
    bcdic['deleteAllSupportsButton'].on_click(partial(delAllSupportsOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, \
         solModule=soldic, ssetCDS=scds, modeCDS=mcds, debugInfo=debug))
    bcdic['showSupportInfoToggle'].on_change('active', partial(toggleSupportInfo, bcModule=bcdic))

    soldic['checkModelButton'].on_click(partial(checkModelOnClick, nModule=ndic, elModule=edic, bcModule=bcdic, solModule=soldic, modeCDS=mcds))
    soldic['solveButton'].on_click(partial(solveOnClick, elModule=edic, bcModule=bcdic, solModule=soldic, modeCDS=mcds))
    soldic['modeSpinner'].on_change('value', partial(changeEigenmode, solModule=soldic, modeCDS=mcds))
    soldic['scaleSlider'].on_change('value', partial(changeScale, elModule=edic, solModule=soldic, modeCDS=mcds))
    soldic['flipButton'].on_click(partial(flip, elModule=edic, solModule=soldic, modeCDS=mcds))

    """
    Layout
    """
    nodeLayout = row(column(ndic['nIDWidget'], ndic['nXWidget'], ndic['nYWidget'], ndic['addNodeButton']), \
        column(Spacer(width=100,height=17), ndic['assignDOFsButton'], Spacer(width=100,height=ndic['nXWidget'].height+10), \
            ndic['delNodeNumWidget'], ndic['delNodeButton'], ndic['delAllNodesButton']), Spacer(width=25), ndic['divNodes'])

    elemLayout =  row(column(edic['enaWidget'], edic['hinaWidget'], edic['eYoungWidget'], edic['eAreaWidget'], edic['addElemButton']), \
                    column(edic['enbWidget'], edic['hinbWidget'], edic['eDensityWidget'], edic['eInertiaWidget']), \
                    column(edic['eIDWidget'], Spacer(width=100,height=47), edic['assembleButton'], edic['delElNumWidget'], \
                         edic['delElemButton'], edic['delAllElemButton']), \
                             Spacer(width=25), edic['divElements'])

    bcLayout = row(column(bcdic['rbg'], bcdic['rbgDiv'], row(column(bcdic['addToNodeWidget'], bcdic['addSupportButton']), Spacer(width=150),\
        column(bcdic['deleteFromNodeWidget'], bcdic['deleteSupportButton'], bcdic['deleteAllSupportsButton']) )), \
        Spacer(width=20), bcdic['divSupports'])

    solLayout = column(row(soldic['checkModelButton'], soldic['solveButton']), \
        row(soldic['modeSpinner'], Spacer(width=100), \
            soldic['scaleSlider'], \
            column(Spacer(height=10), soldic['flipButton'])), \
        soldic['divSolver'])

    plotLayout = column( row(Spacer(width = 30), ndic['nodeLabelsToggle'], Spacer(width=10), edic['elemLabelsToggle']), \
        row(Spacer(width = 30), ndic['showNodeInfoToggle'], Spacer(width=10), edic['showElemInfoToggle'], Spacer(width=10), bcdic['showSupportInfoToggle']), \
        p, Spacer(height=50), row(Spacer(width = 30), solLayout))

    layout = row(column(nodeLayout, elemLayout, bcLayout), plotLayout)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc(),debug=True)
