from bokeh.models import ColumnDataSource, LabelSet, CustomJS
from bokeh.plotting import figure

def makePlot(nsetCDS, elsetCDS, ssetCDS):
    p = figure(width=800, height=600, match_aspect=True)
    ### NODES
    nodeRenderer = p.circle('x', 'y', source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
    nodeLabels = LabelSet(x='x', y='y', text='IDs',
            x_offset=5, y_offset=5, source=nsetCDS, render_mode='canvas')
    p.add_layout(nodeLabels)
    nodeRenderer.js_on_change('visible', CustomJS(args=dict(ls=nodeLabels), code="ls.visible = cb_obj.visible;"))
    ### ELEMENTS
    p.multi_line(xs='x', ys='y', source=elsetCDS, line_width=5, line_color='black', legend_label="Elements")
    ### SUPPORT
    supportRenderer = p.scatter('x', 'y', marker="mtype", source=ssetCDS, size=20, color="red", legend_label="Supports")
    supportLabels = LabelSet(x='x', y='y', text='types',
            x_offset=5, y_offset=5, source=ssetCDS, render_mode='canvas')
    # p.add_layout(supportLabels)
    supportRenderer.js_on_change('visible', CustomJS(args=dict(ls=supportLabels), code="ls.visible = cb_obj.visible;"))
    ### LEGEND
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    return p

def createPlotLayout(nodeset, elemset, bcset):
    exNodes, eyNodes, idlist = nodeset.getExEy()
    ncds = ColumnDataSource({'x':exNodes, 'y':eyNodes, 'IDs':idlist})
    exElems, eyElems = elemset.getExEy()
    ecds = ColumnDataSource({'x':exElems, 'y':eyElems})
    exSupp, eySupp, typelist, markertypes = bcset.getExEy()
    scds = ColumnDataSource({'x':exSupp, 'y':eySupp, 'types':typelist, 'mtype':markertypes})
    p = makePlot(ncds, ecds, scds)

    return p, ncds, ecds, scds
