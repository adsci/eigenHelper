from bokeh.models import ColumnDataSource, LabelSet, CustomJS, Label
from bokeh.plotting import figure


def makePlot(nsetCDS, elsetCDS, ssetCDS, modeCDS, frequencyText):
    p = figure(width=800, height=600, match_aspect=True)
    ### NODES
    nodeRenderer = p.circle('x', 'y', source=nsetCDS, size=7, color="navy", alpha=0.5, legend_label="Nodes")
    nodeLabels = LabelSet(x='x', y='y', text='IDs', text_color="purple", text_alpha=0.6, text_font_size='14px',
            x_offset=10, y_offset=10, source=nsetCDS, render_mode='canvas', visible=True)
    p.add_layout(nodeLabels)
    nodeRenderer.js_on_change('visible', CustomJS(args=dict(ls=nodeLabels), code="ls.visible = cb_obj.visible;"))
    ### ELEMENTS
    elRenderer = p.multi_line(xs='x', ys='y', source=elsetCDS, line_width=2, alpha=0.5, line_color='black', legend_label="Elements")
    elLabels = LabelSet(x='xmid', y='ymid', text='IDs', text_color="red", text_alpha=0.6, text_font_size='14px',
            x_offset=10, y_offset=10, source=elsetCDS, render_mode='canvas', visible=True)
    p.add_layout(elLabels)
    elRenderer.js_on_change('visible', CustomJS(args=dict(ls=elLabels), code="ls.visible = cb_obj.visible;"))
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
    p.add_layout(frequencyText)
    ### LABEL SETS
    lsets = {'nodes':nodeLabels, 'elements':elLabels}
    return p, lsets

def createPlotLayout(nodeset, elemset, bcset):
    #Nodes CDS
    exNodes, eyNodes, idlist = nodeset.getExEy()
    ncds = ColumnDataSource({'x':exNodes, 'y':eyNodes, 'IDs':idlist})
    #Elements CDS
    exElems, eyElems, ids, xmid, ymid = elemset.getExEy()
    ecds = ColumnDataSource({'x':exElems, 'y':eyElems, 'IDs':ids, 'xmid':xmid, 'ymid':ymid})
    #Support CDS
    exSupp, eySupp, wSupp, hSupp, urls = bcset.getExEy(horizontal=False)
    scdsVertical = ColumnDataSource({'x':exSupp, 'y':eySupp, 'w':wSupp, 'h':hSupp, 'urls':urls})
    exSupp, eySupp, wSupp, hSupp, urls = bcset.getExEy(horizontal=True)
    scdsHotizontal = ColumnDataSource({'x':exSupp, 'y':eySupp, 'w':wSupp, 'h':hSupp, 'urls':urls})
    scds = [scdsVertical, scdsHotizontal]
    #label freqText must be created and updated oustide of the plot
    freqText = Label(x=50, y=50, x_units='screen', y_units='screen',
        text='', text_color='blue', text_font='helvetica', text_font_style='bold', text_alpha=0.7,
        render_mode='css', border_line_color='black', border_line_alpha=0,
        background_fill_color='white', border_line_width=2, background_fill_alpha=1.0, visible=False)
    #Eigenmode CDS
    modecds = ( ColumnDataSource({'x':[], 'y':[]}), freqText )
    p, lsets = makePlot(ncds, ecds, scds, modecds[0], modecds[1])

    return p, lsets, ncds, ecds, scds, modecds
