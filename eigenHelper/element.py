from bokeh.models import Div, NumericInput, Button
from utils import *
import calfem.core as cfc

class Element():
    def __init__(self, id, nodeA, nodeB, prop):
        self.id = id
        self.na = nodeA
        self.nb = nodeB
        self.edof = np.concatenate((self.na.getDOFs(),self.nb.getDOFs()))
        self.properties = prop
        self.computeMatrices()

    def getExEy(self):
        ex = np.array([self.na.getX(), self.nb.getX()])
        ey = np.array([self.na.getY(), self.nb.getY()])
        return ex, ey

    def getNodes(self):
        return [self.na.getID(), self.nb.getID()]

    def getProp(self):
        return self.properties

    def getEdof(self):
        return self.edof

    def getID(self):
        return self.id

    def computeMatrices(self):
        ex, ey = self.getExEy()
        props = self.getProp()
        ep = [props['E'], props['A'], props['I'], props['rho']*props['A']]
        self.Ke, self.Me = cfc.beam2d(ex, ey, ep)

    def printInfo(self, debug=False):
        if debug:
            info = f"Element {self.getID()} with nodes {str(self.getNodes())}\n"
            info += f"with edof = {self.getEdof()}\n"
            info += f"Properties: E={self.getProp()['E']} Pa, rho={self.getProp()['rho']} kg/m3, A={self.getProp()['A']} m2, I={self.getProp()['I']} m4 \n"
            info += f"Stiffness matrix: \n{self.Ke} \n"
            info += f"Mass matrix: \n{self.Me} \n"
            info += "<br>"
            return info
        else:
            info = f"Element {self.getID()} with nodes {str(self.getNodes())}\n"
            return info


class ElementSet(EntitySet):
    def foundNodes(self,n1,n2):
        for elem in self.members:
            if ((elem.na is n1) and (elem.nb is n2)) or ((elem.na is n2) and (elem.nb is n1)):
                return True
        return False

    def getExEy(self):
        ex = []
        ey = []
        for elem in self.members:
            iex, iey = elem.getExEy()
            ex.append(iex)
            ey.append(iey)
        return ex, ey


def createElement(elset, nset, id, na, nb, elprop):
    fndA, _ = nset.foundID(na.getID())
    fndB, _ = nset.foundID(nb.getID())
    if not (fndA and fndB):
        return False
    fndNds = elset.foundNodes(na,nb)
    fndID, _ = elset.foundID(id)
    if not (fndNds or fndID) and not (na is nb):
        newElement = Element(id,na,nb,elprop)
        return newElement
    return False

def updateElementData(elemset, elemCDS):
    ex, ey = elemset.getExEy()
    elemCDS.data = {'x':ex, 'y':ey}

def updateElementText(divText, elemset, debugInfo):
    divText.text = "<b>Elements</b>:<br>" + elemset.printInfo(debugInfo)

def activateElementModule(edict):
    for key, val in edict.items():
        val.disabled = False

def deactivateElementModule(edict):
    for key, val in edict.items():
        val.disabled = True
    edict['divElements'].disabled = False

"""
Element module callbacks
"""
def addElemOnClick(nodeset, elemset, eidWidget, naWidget, nbWidget, youngWidget, densityWidget, areaWidget, inertiaWidget,\
     dtext, elemCDS, debugInfo):
    if eidWidget.value <= 0:
        return
    #check whether the element can be added
    na = nodeset.getEntityWithID(naWidget.value)
    nb = nodeset.getEntityWithID(nbWidget.value)
    if not (na and nb):
        return
    nElement = createElement(elemset, nodeset, eidWidget.value, na, \
        nb, {'E':youngWidget.value, 'rho':densityWidget.value, 'A':areaWidget.value, 'I':inertiaWidget.value})
    if not nElement:
        return
    elemset.add(nElement)
    eidWidget.value = elemset.getNextID()
    updateElementData(elemset,elemCDS)
    updateElementText(dtext, elemset, debugInfo)
    # dtext.text= "<b>Elements</b>:<br>" + elemset.printInfo(debugInfo)

def delElemOnClick(elemset, eidWidget, delElWidget, dtext, elemCDS, debugInfo):
    if (not elemset.members) or (not elemset.foundID(delElWidget.value)[0]):
        return
    elemset.deleteEntityWithID(delElWidget.value)
    delElWidget.value = 0
    eidWidget.value = elemset.getNextID()
    updateElementData(elemset, elemCDS)
    updateElementText(dtext, elemset, debugInfo)
    # dtext.text=elemset.printInfo(debugInfo)

def delAllElemOnClick(elemset, eidWidget, dtext, elemCDS, debugInfo):
    elemset.clear()
    eidWidget.value = elemset.getNextID()
    updateElementData(elemset, elemCDS)
    updateElementText(dtext, elemset, debugInfo)


"""
Element module layout
"""
def createElementLayout(debug=False):
    eset = ElementSet()
    eIDWidget = NumericInput(value=1, title="Element ID:",mode='int', width=50,height=50, disabled=True)
    enaWidget = NumericInput(value=0, title="Node A:",mode='int', width=50,height=50, disabled=True)
    enbWidget = NumericInput(value=0, title="Node B:",mode='int', width=50, disabled=True)
    eYoungWidget = NumericInput(value=1, title="E [Pa]",mode='int', width=100,height=50, disabled=True)
    eDensityWidget = NumericInput(value=1, title="rho [kg/m^3]:",mode='int', width=100,height=50, disabled=True)
    eAreaWidget = NumericInput(value=1, title="A [m^2]:",mode='int', width=100,height=50, disabled=True)
    eInertiaWidget = NumericInput(value=1, title="I [m^4]:",mode='int', width=100,height=50, disabled=True)
    delElNumWidget = NumericInput(value=0, title="Element to be deleted:",mode='int', width=50, disabled=True)
    addElemButton = Button(label="Add Element", button_type="primary", width=100, disabled=True )
    delElemButton = Button(label="Delete Element", button_type="warning", width=120, disabled=True )
    delAllElemButton = Button(label="Delete All Elements", button_type="danger", width=120, disabled=True )
    divElements = Div(text= "<b>Elements</b>:<br>", width=350, height=300)

    elemLayoutDict = {'eset':eset, 'eIDWidget':eIDWidget, 'enaWidget':enaWidget, 'enbWidget':enbWidget, \
        'eYoungWidget':eYoungWidget, 'eDensityWidget':eDensityWidget, 'eAreaWidget':eAreaWidget, 'eInertiaWidget':eInertiaWidget, \
        'delElNumWidget':delElNumWidget, 'addElemButton':addElemButton, 'delElemButton':delElemButton, \
        'delAllElemButton':delAllElemButton, 'divElements':divElements}
    return elemLayoutDict