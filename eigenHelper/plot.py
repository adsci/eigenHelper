from bokeh.models import ColumnDataSource, LabelSet, CustomJS
from bokeh.plotting import figure

def makePlot(nsetCDS, elsetCDS):
    p = figure(width=800, height=800, match_aspect=True)
    ### NODES
    renderer = p.circle('x', 'y', source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
    labels = LabelSet(x='x', y='y', text='IDs',
            x_offset=5, y_offset=5, source=nsetCDS, render_mode='canvas')
    p.add_layout(labels)
    renderer.js_on_change('visible', CustomJS(args=dict(ls=labels), code="ls.visible = cb_obj.visible;"))
    ### ELEMENTS
    p.multi_line(xs='x', ys='y', source=elsetCDS, line_width=5, line_color='black', legend_label="Elements")
    ### LEGEND
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    return p

def createPlotLayout(nodeset, elemset):
    exNodes, eyNodes, idlist = nodeset.getExEy()
    ncds = ColumnDataSource({'x':exNodes, 'y':eyNodes, 'IDs':idlist})
    exElems, eyElems = elemset.getExEy()
    ecds = ColumnDataSource({'x':exElems, 'y':eyElems})
    p = makePlot(ncds, ecds)

    return p, ncds, ecds
