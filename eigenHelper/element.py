from bokeh.models import Div, NumericInput, Button, CheckboxGroup, Toggle
from utils import *
import node
import bc
import solver
import howto

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
        return [self.na.getName(), self.nb.getName()]

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
        self.ddofs = np.array([], dtype=np.int32)
        self.potentialddofs = []

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

    def getIDs(self):
        ids = []
        for elem in self.members:
            ids.append(str(elem.getID()))
        return ids

    def getMidCoords(self):
        xmid = []
        ymid = []
        ex, ey = self.getExEy()
        for i, _iex in enumerate(self.members):
            xmid.append(np.mean(ex[i]))
            ymid.append(np.mean(ey[i]))
        return xmid, ymid

    def getProperties(self):
        E = []
        A = []
        I = []
        rho = []
        for elem in self.members:
            iprop = elem.getProp()
            E.append(iprop['E'])
            A.append(iprop['A'])
            I.append(iprop['I'])
            rho.append(iprop['rho'])
        return E, A, I, rho

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

    def setNdof(self):
        curmax = np.NINF
        for elem in self.members:
            maxdof = np.max(elem.getEdof())
            if maxdof > curmax:
                curmax = maxdof
        self.ndof = curmax

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
        self.ddofs = np.array([], dtype=np.int32)
        self.potentialddofs = []

    def checkDanglingDOFs(self, potentialDofs):
        edofs = self.getModelEdof()
        for potentialDanglingDof in potentialDofs:
            if potentialDanglingDof not in edofs:
                self.addDanglingDOF(potentialDanglingDof)

    def addDanglingDOF(self, dof):
        self.ddofs = np.unique(np.append(self.ddofs,dof))


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
    ids = elemset.getIDs()
    xmid, ymid = elemset.getMidCoords()
    E, A, I, rho = elemset.getProperties()
    elemCDS.data = {'x':ex, 'y':ey, 'IDs':ids, 'xmid':xmid, 'ymid':ymid, 'E':E, 'A':A, 'I':I, 'rho':rho }

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
    elModule['showElemInfoToggle'].disabled = False
    elModule['elemLabelsToggle'].disabled = False

def clearElementModule(elModule, htModule, elemCDS, debugInfo):
    elModule['eset'].clear()
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    elModule['enaWidget'].value = 1
    elModule['enbWidget'].value = 2
    elModule['assembleButton'].disabled = False
    updateElementData(elModule['eset'], elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    htModule['colors'][2] = 'red'
    howto.updateHowtoDiv(htModule)



"""
Element module callbacks
"""
def addElemOnClick(nModule, elModule, solModule, nodeCDS, elemCDS, debugInfo):
    if elModule['eIDWidget'].value <= 0:
        return
    #check whether the element can be added
    na = nModule['nset'].getEntityWithID(elModule['enaWidget'].value)
    nb = nModule['nset'].getEntityWithID(elModule['enbWidget'].value)
    elprop = {'E':elModule['eYoungWidget'].value, 'rho':elModule['eDensityWidget'].value, 'A':elModule['eAreaWidget'].value, 'I':elModule['eInertiaWidget'].value}
    if not (na and nb):
        return
    #create the element - first check for possible hinges
    if not (elModule['hinaWidget'].active or elModule['hinbWidget'].active):
        nElement = createElement(elModule['eset'], nModule['nset'], elModule['eIDWidget'].value, na, nb, elprop)
    else: #find which node(s) should be a hinge
        #duplicate them and add rotational dof
        if (elModule['hinaWidget'].active):
            hingeNode, dDof = na.duplicateAsHinge(nModule['nset'].getNextID(), nModule['nset'].getNextDOF())
            nModule['nset'].add(hingeNode)
            nModule['nIDWidget'].value = nModule['nset'].getNextID()
            elModule['eset'].potentialddofs.append(dDof)
            na = hingeNode
        if (elModule['hinbWidget'].active):
            hingeNode, dDof = nb.duplicateAsHinge(nModule['nset'].getNextID(), nModule['nset'].getNextDOF())
            nModule['nset'].add(hingeNode)
            nModule['nIDWidget'].value = nModule['nset'].getNextID()
            elModule['eset'].potentialddofs.append(dDof)
            nb = hingeNode
        #create element with new rotational dof
        nElement = createElement(elModule['eset'], nModule['nset'], elModule['eIDWidget'].value, na, nb, elprop)
        #TODO: plot hinge symbol
        node.updateCoordData(nModule['nset'], nodeCDS)
        node.updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)
        elModule['hinaWidget'].active = []
        elModule['hinbWidget'].active = []
    if not nElement:
        return
    elModule['eset'].add(nElement)
    elModule['eset'].setNdof()
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    updateElementData(elModule['eset'],elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    elModule['assembleButton'].disabled = False
    solModule['solveButton'].disabled = True

def delElemOnClick(nModule, elModule, bcModule, solModule, htModule, nodeCDS, elemCDS, modeCDS, debugInfo):
    if (not elModule['eset'].members) or (not elModule['eset'].foundID(elModule['delElNumWidget'].value)[0]):
        return
    #remove duplicated hinge nodes at element removal
    elToDelete = elModule['eset'].getEntityWithID(elModule['delElNumWidget'].value)
    nodes = [elToDelete.na, elToDelete.nb]
    for n in nodes:
        if n.hinge:
            nModule['nset'].deleteEntityWithID(n.getID())
            node.updateCoordData(nModule['nset'], nodeCDS)
            node.updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)
    #remove the element
    elModule['eset'].deleteEntityWithID(elModule['delElNumWidget'].value)
    elModule['delElNumWidget'].value = 0
    elModule['eIDWidget'].value = elModule['eset'].getNextID()
    updateElementData(elModule['eset'], elemCDS)
    updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    bc.deactivateBCModule(bcModule, htModule)
    elModule['assembleButton'].disabled = False
    htModule['colors'][2] = 'red'
    howto.updateHowtoDiv(htModule)
    solver.checkModelOnClick(nModule, elModule, bcModule, solModule, htModule, modeCDS)

def delAllElemOnClick(nModule, elModule, bcModule, solModule, htModule, nodeCDS, elemCDS, ssetCDS, modeCDS, debugInfo):
    bc.clearBCModule(bcModule, htModule, ssetCDS, debugInfo)
    bc.deactivateBCModule(bcModule, htModule)
    clearElementModule(elModule, htModule, elemCDS, debugInfo)
    nModule['nset'].removeHinges()
    node.updateCoordData(nModule['nset'], nodeCDS)
    node.updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)
    solver.checkModelOnClick(nModule, elModule, bcModule, solModule, htModule, modeCDS)
    node.activateNodeModule(nModule, debugInfo)

def assembleOnClick(nModule, elModule, bcModule, solModule, htModule, nodeCDS, debugInfo):
    if elModule['eset'].members:
        #check for dangling nodes, delete them and flag dangling rotational dofs
        elModule['eset'].checkDanglingDOFs(elModule['eset'].potentialddofs)
        nModule['nset'].cleanUpAfterHinges(elModule['eset'].ddofs)
        node.updateCoordData(nModule['nset'], nodeCDS)
        node.updateNodeText(nModule['divNodes'], nModule['nset'], True, debugInfo)
        #assemble stiffness and mass matrices
        elModule['eset'].assemble()
        updateElementText(elModule['divElements'], elModule['eset'], True, debugInfo)
        htModule['colors'][2] = 'green'
        howto.updateHowtoDiv(htModule)
        bc.activateBCModule(bcModule)
        elModule['assembleButton'].disabled = True
        solModule['solveButton'].disabled = True

def toggleElementLabels(attr, old, new, labels):
    hide(labels['elements']) if new else show(labels['elements'])

def toggleElementInfo(attr, old, new, elModule):
    show(elModule['divElements']) if new else hide(elModule['divElements'])

"""
Element module layout
"""
def createElementLayout(debug=False):
    eset = ElementSet()
    eIDWidget = NumericInput(value=1, title="Element ID:",mode='int', width=50,height=50, disabled=True)
    enaWidget = NumericInput(value=1, title="Node A:",mode='int', width=50,height=50, disabled=True)
    enbWidget = NumericInput(value=2, title="Node B:",mode='int', width=50, disabled=True)
    hinaWidget = CheckboxGroup(labels=['Hinge at A'], active=[], width=100, disabled=True)
    hinbWidget = CheckboxGroup(labels=['Hinge at B'], active=[], width=100, disabled=True)
    eYoungWidget = NumericInput(value=3e10, title="E [Pa]",mode='float', width=100,height=50, disabled=True)
    eDensityWidget = NumericInput(value=2500, title="\u03C1 [kg/m\u00b3]:",mode='float', width=100,height=50, disabled=True)
    eAreaWidget = NumericInput(value=0.1030e-2, title="A [m\u00b2]:",mode='float', width=100,height=50, disabled=True)
    eInertiaWidget = NumericInput(value=0.0171e-4, title="I [m\u2074]:",mode='float', width=100,height=50, disabled=True)
    delElNumWidget = NumericInput(value=0, title="Element to be deleted:",mode='int', width=50, disabled=True)
    addElemButton = Button(label="Add Element", button_type="primary", width=100, disabled=True )
    delElemButton = Button(label="Remove Element", button_type="warning", width=120, disabled=True )
    delAllElemButton = Button(label="Remove All Elements", button_type="warning", width=120, disabled=True )
    assembleButton = Button(label="Go to Define Supports", button_type="success", width=50, disabled=True )
    elemLabelsToggle= Toggle(label="Hide Element Numbers", button_type='default', width=150)
    showElemInfoToggle = Toggle(label="Show Element Info", button_type='default', width=150)
    divElements = Div(text= "<b>Elements</b>:<br>", width=300, height=800, visible=False)
    divLine = Div(text= '<hr noshade width="400"><b>Define elements:</b>', visible=True)


    elemLayoutDict = {'eset':eset, 'eIDWidget':eIDWidget, 'enaWidget':enaWidget, 'enbWidget':enbWidget, \
        'hinaWidget':hinaWidget, 'hinbWidget':hinbWidget, \
        'eYoungWidget':eYoungWidget, 'eDensityWidget':eDensityWidget, 'eAreaWidget':eAreaWidget, 'eInertiaWidget':eInertiaWidget, \
        'delElNumWidget':delElNumWidget, 'addElemButton':addElemButton, 'delElemButton':delElemButton, \
        'delAllElemButton':delAllElemButton, 'assembleButton': assembleButton, 'divElements':divElements, \
        'elemLabelsToggle':elemLabelsToggle, 'showElemInfoToggle':showElemInfoToggle, 'divLine':divLine}
    return elemLayoutDict