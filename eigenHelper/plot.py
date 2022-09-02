from bokeh.models import ColumnDataSource, LabelSet, CustomJS, ImageURL
from bokeh.plotting import figure


def makePlot(nsetCDS, elsetCDS, ssetCDS, modeCDS):
    p = figure(width=800, height=600, match_aspect=True)
    ### NODES
    nodeRenderer = p.circle('x', 'y', source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
    nodeLabels = LabelSet(x='x', y='y', text='IDs',
            x_offset=10, y_offset=10, source=nsetCDS, render_mode='canvas')
    p.add_layout(nodeLabels)
    nodeRenderer.js_on_change('visible', CustomJS(args=dict(ls=nodeLabels), code="ls.visible = cb_obj.visible;"))
    ### ELEMENTS
    p.multi_line(xs='x', ys='y', source=elsetCDS, line_width=2, alpha=0.5, line_color='black', legend_label="Elements")
    ### SUPPORT
    p.image_url(url='urls', x='x', y='y', w='w', h='h', w_units='screen', h_units='screen', \
        anchor='top_center', source=ssetCDS[0], legend_label="Supports")
    p.image_url(url='urls', x='x', y='y', w='w', h='h', w_units='screen', h_units='screen', \
        anchor='center_left', source=ssetCDS[1], legend_label="Supports")
    ### EIGENMODES
    p.multi_line(xs='x', ys='y', source=modeCDS, line_width=5, line_color='black', legend_label="Eigenmode")
    ### LEGEND
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    return p

def createPlotLayout(nodeset, elemset, bcset, solution):
    #Nodes CDS
    exNodes, eyNodes, idlist = nodeset.getExEy()
    ncds = ColumnDataSource({'x':exNodes, 'y':eyNodes, 'IDs':idlist})
    #Elements CDS
    exElems, eyElems = elemset.getExEy()
    ecds = ColumnDataSource({'x':exElems, 'y':eyElems})
    #Support CDS
    exSupp, eySupp, wSupp, hSupp, urls = bcset.getExEy(horizontal=False)
    scdsVertical = ColumnDataSource({'x':exSupp, 'y':eySupp, 'w':wSupp, 'h':hSupp, 'urls':urls})
    exSupp, eySupp, wSupp, hSupp, urls = bcset.getExEy(horizontal=True)
    scdsHotizontal = ColumnDataSource({'x':exSupp, 'y':eySupp, 'w':wSupp, 'h':hSupp, 'urls':urls})
    scds = [scdsVertical, scdsHotizontal]
    #Eigenmode CDS
    modecds = ColumnDataSource({'x':[], 'y':[]})
    p = makePlot(ncds, ecds, scds, modecds)

    return p, ncds, ecds, scds, modecds
