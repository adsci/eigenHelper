from bokeh.io import curdoc
from bokeh.models import Div

def modify_doc(doc):
    div = Div(text="""
    eigenHelper is a browser-based app visualising eigenmodes of simple frame structures.
    The app is intented to be used by students learning to solve eigenvalue problems for 
    free vibration of frame structures""", width=300, height=100)
    doc.add_root(div)

modify_doc(curdoc())