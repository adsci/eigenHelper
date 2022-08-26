from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from functools import partial
from utils import *
from node import *
from element import *
from plot import *

def modify_doc(doc, debug=False):

    #Create Node module
    ndic = createNodeLayout(debug)

    #Create Element module
    edic = createElementLayout(debug)

    #Create Plot module
    p, ncds, ecds = createPlotLayout(ndic['nset'], edic['eset'])

    """
    Handlers
    """
    ndic['addNodeButton'].on_click(partial(addNodeOnClick, nodeset=ndic['nset'], nxWidget=ndic['nXWidget'], nyWidget=ndic['nYWidget'],\
         nidInput=ndic['nIDWidget'], dtext=ndic['divNodes'], nodeCDS=ncds, debugInfo=debug))
    ndic['delNodeButton'].on_click(partial(delNodeOnClick, nodeset=ndic['nset'], nidWidget=ndic['nIDWidget'], delNodeWidget=ndic['delNodeNumWidget'], \
        dtext=ndic['divNodes'], nodeCDS=ncds, debugInfo=debug))
    ndic['assignDOFsButton'].on_click(partial(assignDOFsOnClick, nodeset=ndic['nset'], dtext=ndic['divNodes'], debugInfo=debug))

    edic['addElemButton'].on_click(partial(addElemOnClick, nodeset=ndic['nset'], elemset=edic['eset'], eidWidget=edic['eIDWidget'],\
        naWidget=edic['enaWidget'], nbWidget=edic['enbWidget'], youngWidget=edic['eYoungWidget'], densityWidget=edic['eDensityWidget'],\
        areaWidget=edic['eAreaWidget'], inertiaWidget=edic['eInertiaWidget'], dtext=edic['divElements'], elemCDS=ecds, debugInfo=debug))
    edic['delElemButton'].on_click(partial(delElemOnClick, elemset=edic['eset'], eidWidget=edic['eIDWidget'], delElWidget=edic['delElNumWidget'],\
         dtext=edic['divElements'], elemCDS=ecds, debugInfo=debug))

    """
    Layout
    """
    nodeLayout = row(column(ndic['nIDWidget'], ndic['nXWidget'], ndic['nYWidget'], ndic['addNodeButton']), \
        column(Spacer(width=100,height=17), ndic['assignDOFsButton'], Spacer(width=100,height=ndic['nXWidget'].height+10), \
            ndic['delNodeNumWidget'], ndic['delNodeButton']), Spacer(width=25), ndic['divNodes'])
    elemLayout =  row(column(edic['enaWidget'], edic['eYoungWidget'], edic['eAreaWidget'], edic['addElemButton']), \
                    column(edic['enbWidget'], edic['eDensityWidget'], edic['eInertiaWidget']), \
                    column(edic['eIDWidget'], Spacer(width=100,height=edic['eIDWidget'].height+10), edic['delElNumWidget'], edic['delElemButton']) ,\
                         Spacer(width=25), edic['divElements'])

    layout = row(column(nodeLayout, elemLayout), p)
    doc.add_root(layout)
    doc.title = "eigenHelper"

modify_doc(curdoc(),debug=True)
