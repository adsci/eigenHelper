from bokeh.models import Div, NumericInput, Button
from utils import *
from bc import activateBCModule, deactivateBCModule, clearBCModule
from solver import checkModelOnClick

class Element():
    def __init__(self, id, nodeA, nodeB, prop):
        self.id = id
        self.na = nodeA
        self.nb = nodeB
        self.edof = np.concatenate((self.na.getDOFs(),self.nb.getDOFs()))
        self.properties = prop
        self.Ke, self.Me = self.computeMatrices()

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

    def getElementStiffnessMatrix(self):
        return self.Ke

    def getElementMassMatrix(self):
        return self.Me

    def computeMatrices(self):
        ex, ey = self.getExEy()
        props = self.getProp()
        ep = [props['E'], props['A'], props['I'], props['rho']*props['A']]
        Ke, Me = cfc.beam2d(ex, ey, ep)
        return Ke, Me

    def printInfo(self, debug=False):
        if debug:
            info = f"Element {self.getID()} with nodes {str(self.getNodes())}\n"
            info += f"with edof = {self.getEdof()}\n"
            # info += f"Properties: E={self.getProp()['E']} Pa, rho={self.getProp()['rho']} kg/m3, A={self.getProp()['A']} m2, I={self.getProp()['I']} m4 \n"
            # info += f"Stiffness matrix: \n{self.Ke} \n"
            # info += f"Mass matrix: \n{self.Me} \n"
            # info += "<br>"
            return info
        else:
            info = f"Element {self.getID()} with nodes {str(self.getNodes())}\n"
            return info


class ElementSet(EntitySet):
    def __init__(self):
        EntitySet.__init__(self)
        self.K = []
        self.M = []
        self.ndof = 0
        self.edof = []

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

    def getStiffnessMatrix(self):
        return self.K

    def getMassMatrix(self):
        return self.M

    def getModelEdof(self):
        edof = np.zeros((self.getSize(),6), dtype=np.int32)
        for nel, element in enumerate(self.members):
            edof[nel,:] = element.getEdof()
        self.edof = edof
        return self.edof

    def assemble(self):
        self.K = np.zeros((self.ndof, self.ndof))
        self.M = np.zeros((self.ndof, self.ndof))
        for elem in self.members:
            cfc.assem(elem.getEdof(), self.getStiffnessMatrix(), elem.getElementStiffnessMatrix())
            cfc.assem(elem.getEdof(), self.getMassMatrix(), elem.getElementMassMatrix())

    def clear(self):
        EntitySet.clear(self)
        self.K = []
        self.M = []
        self.ndof = 0
        self.edof = []


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

def updateElementText(divText, elemset, readyFlag, debugInfo):
    newText = ['<b>Elements</b>:<br>']
    newText += elemset.printInfo(debugInfo)
    if not readyFlag:
        newText.append('<br><p style="color:red"><b>Click Continue when node input ready</b></p>')
    else:
        newText.append('<br><p style="color:green"><b>Ready for boundary condition input</b></p>')
    divText.text = ''.join(newText)

def activateElementModule(elModule, debugInfo):
    for _, val in elModule.items():
        val.disabled = False
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)

def deactivateElementModule(elModule):
    for _, val in elModule.items():
        val.disabled = True
    elModule['divElements'].disabled = False

def clearElementModule(elModule, elemCDS, debugInfo):
    elModule['eset'].clear()
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    elModule['assembleButton'].disabled = False
    updateElementData(elModule['eset'], elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)



"""
Element module callbacks
"""
def addElemOnClick(nModule, elModule, solModule, elemCDS, debugInfo):
    if elModule['eIDWidget'].value <= 0:
        return
    #check whether the element can be added
    na = nModule['nset'].getEntityWithID(elModule['enaWidget'].value)
    nb = nModule['nset'].getEntityWithID(elModule['enbWidget'].value)
    if not (na and nb):
        return
    nElement = createElement(elModule['eset'], nModule['nset'], elModule['eIDWidget'].value, na, \
        nb, {'E':elModule['eYoungWidget'].value, 'rho':elModule['eDensityWidget'].value, 'A':elModule['eAreaWidget'].value, 'I':elModule['eInertiaWidget'].value})
    if not nElement:
        return
    elModule['eset'].add(nElement)
    elModule['eset'].ndof = np.max(nElement.getEdof())
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    updateElementData(elModule['eset'],elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    elModule['assembleButton'].disabled = False
    solModule['solveButton'].disabled = True

def delElemOnClick(nModule, elModule, bcModule, solModule, elemCDS, modeCDS, debugInfo):
    if (not elModule['eset'].members) or (not elModule['eset'].foundID(elModule['delElNumWidget'].value)[0]):
        return
    elModule['eset'].deleteEntityWithID(elModule['delElNumWidget'].value)
    elModule['delElNumWidget'].value = 0
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    updateElementData(elModule['eset'], elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    deactivateBCModule(bcModule)
    elModule['assembleButton'].disabled = False
    checkModelOnClick(nModule, elModule, bcModule, solModule, modeCDS)

def delAllElemOnClick(nModule, elModule, bcModule, solModule, elemCDS, ssetCDS, modeCDS, debugInfo):
    clearBCModule(bcModule, ssetCDS, debugInfo)
    deactivateBCModule(bcModule)
    clearElementModule(elModule, elemCDS, debugInfo)
    checkModelOnClick(nModule, elModule, bcModule, solModule, modeCDS)

def assembleOnClick(elModule, bcModule, solModule, debugInfo):
    if elModule['eset'].members:
        elModule['eset'].assemble()
        updateElementText(elModule['divElements'], elModule['eset'], True, debugInfo)
        activateBCModule(bcModule)
        elModule['assembleButton'].disabled = True
        solModule['solveButton'].disabled = True

"""
Element module layout
"""
def createElementLayout(debug=False):
    eset = ElementSet()
    eIDWidget = NumericInput(value=1, title="Element ID:",mode='int', width=50,height=50, disabled=True)
    enaWidget = NumericInput(value=1, title="Node A:",mode='int', width=50,height=50, disabled=True)
    enbWidget = NumericInput(value=2, title="Node B:",mode='int', width=50, disabled=True)
    eYoungWidget = NumericInput(value=3e10, title="E [Pa]",mode='float', width=100,height=50, disabled=True)
    eDensityWidget = NumericInput(value=2500, title="rho [kg/m^3]:",mode='float', width=100,height=50, disabled=True)
    eAreaWidget = NumericInput(value=0.1030e-2, title="A [m^2]:",mode='float', width=100,height=50, disabled=True)
    eInertiaWidget = NumericInput(value=0.0171e-4, title="I [m^4]:",mode='float', width=100,height=50, disabled=True)
    delElNumWidget = NumericInput(value=0, title="Element to be deleted:",mode='int', width=50, disabled=True)
    addElemButton = Button(label="Add Element", button_type="primary", width=100, disabled=True )
    delElemButton = Button(label="Remove Element", button_type="warning", width=120, disabled=True )
    delAllElemButton = Button(label="Remove All Elements", button_type="danger", width=120, disabled=True )
    assembleButton = Button(label="Continue", button_type="success", width=50, disabled=True )
    divElements = Div(text= "<b>Elements</b>:<br>", width=350, height=300)

    elemLayoutDict = {'eset':eset, 'eIDWidget':eIDWidget, 'enaWidget':enaWidget, 'enbWidget':enbWidget, \
        'eYoungWidget':eYoungWidget, 'eDensityWidget':eDensityWidget, 'eAreaWidget':eAreaWidget, 'eInertiaWidget':eInertiaWidget, \
        'delElNumWidget':delElNumWidget, 'addElemButton':addElemButton, 'delElemButton':delElemButton, \
        'delAllElemButton':delAllElemButton, 'assembleButton': assembleButton, 'divElements':divElements}
    return elemLayoutDict