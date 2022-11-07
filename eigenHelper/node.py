"""
Node module with helper function and classes
"""
from bokeh.models import Div, NumericInput, Button, Toggle
from utils import *
from copy import deepcopy
import element
import bc
import solver

class Node():
    def __init__(self,x,y,id):
        self.coords=[x,y]
        self.id = id
        self.dofs = []
        self.dangling = False
        self.hinge = False

    def printInfo(self, debug=False):
        if debug:
            return "Node " +str(self.getID()) + " at " + str(self.getCoords()) + " with DOFs " + str(self.getDOFs())
        else:
            return "Node " +str(self.getID()) + " at " + str(self.getCoords())

    def getID(self):
        return self.id

    def getX(self):
        return self.coords[0]

    def getY(self):
        return self.coords[1]

    def getCoords(self):
        return self.coords

    def setID(self, newID):
        self.id = newID

    def getDOFs(self):
        return self.dofs

    def setDOFs(self, dofArray):
        self.dofs = dofArray

    def duplicateAsHinge(self, hingeid, nextdof):
        hingeNode = deepcopy(self)
        hingeNode.setID(hingeid)
        hingeNode.markAsHinge()
        hingeNode.dofs[-1] = nextdof
        danglingDof = self.markAsDangling()
        return hingeNode, danglingDof

    def markAsDangling(self):
        self.dangling = True
        return self.dofs[-1]

    def markAsHinge(self):
        self.hinge = True

class NodeSet(EntitySet):
    def foundCoords(self,x,y):
        for node in self.members:
            if (abs(node.getX() - x) <= 1e-6) and (abs(node.getY() - y) < 1e-6):
                return True
        return False

    def getExEy(self):
        xlist = []
        ylist = []
        idlist = []
        for node in self.members:
            xlist.append(node.getX())
            ylist.append(node.getY())
            idlist.append(str(node.getID()))
        return (np.array(xlist), np.array(ylist), idlist)

    def assignDOFs(self):
        for i, node in enumerate(self.members):
            node.setDOFs(np.array([3*(i+1)-2, 3*(i+1)-1, 3*(i+1)], dtype=np.int32))

    def getNextDOF(self):
        maxdof = np.NINF
        for member in self.members:
            if max(member.getDOFs()) > maxdof:
                maxdof = max(member.getDOFs())
        if maxdof == np.NINF:
            maxdof = 0
        return maxdof + 1

    def cleanUpAfterHinges(self, danglingDofs):
        flagged = []
        for node in self.members:
            if (node.getDOFs()[-1] in danglingDofs) and (node not in flagged):
                flagged.append(node)

        for danglingNode in flagged:
            self.deleteEntityWithID(danglingNode.getID())


def createNode(nodeset, x, y, id):
    fndCoords = nodeset.foundCoords(x,y)
    fndID, _ = nodeset.foundID(id)
    if not (fndCoords or fndID):
        newNode = Node(x,y,id)
        return newNode
    return False

def updateCoordData(nodeset, nodeCDS):
    ex, ey, ids = nodeset.getExEy()
    nodeCDS.data = {'x':ex, 'y':ey, 'IDs':ids}

def updateNodeText(divText, nodeset, readyFlag, debugInfo):
    newText = ['<b>Nodes</b>:<br>']
    newText += nodeset.printInfo(debugInfo)
    if not readyFlag:
        newText.append('<br><p style="color:red"><b>Click Continue when node input ready</b></p>')
    else:
        newText.append('<br><p style="color:green"><b>Ready for element input</b></p>')
    divText.text = ''.join(newText)

def clearNodeModule(nModule, nodeCDS, debugInfo):
    nModule['nset'].clear()
    nModule['nIDWidget'].value = nModule['nset'].getNextID()
    nModule['nXWidget'].value = 0
    nModule['nYWidget'].value = 0
    nModule['assignDOFsButton'].disabled = False
    updateCoordData(nModule['nset'], nodeCDS)
    updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)



"""
Node module callbacks
"""
def addNodeOnClick(nModule, solModule, nodeCDS, debugInfo):
    if nModule['nIDWidget'].value <= 0:
        return
    #check whether the node can be added
    nNode = createNode(nModule['nset'], float(nModule['nXWidget'].value), float(nModule['nYWidget'].value), nModule['nIDWidget'].value)
    if not nNode:
        return
    nModule['nset'].add(nNode)
    nModule['nIDWidget'].value = nModule['nset'].getNextID()
    updateCoordData(nModule['nset'], nodeCDS)
    updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)
    nModule['assignDOFsButton'].disabled = False
    solModule['solveButton'].disabled = True

def delNodeOnClick(nModule, elModule, bcModule, solModule, nodeCDS, elemCDS, ssetCDS, modeCDS, debugInfo):
    if (not nModule['nset'].members) or (not nModule['nset'].foundID(nModule['delNodeNumWidget'].value)[0]):
        return
    #check for supports and remove
    support = bcModule['sset'].foundAtNode(nModule['delNodeNumWidget'].value)
    if support[0]:
        bcModule['sset'].deleteAtNode(nModule['delNodeNumWidget'].value)
        bc.updateSupportData(bcModule['sset'], ssetCDS)
        bc.updateSupportText(bcModule['divSupports'], bcModule['sset'], False, debugInfo)
    #remove all elements connected to the deleted node
    for el in elModule['eset'].members:
        nodeids = [el.na.getID(), el.nb.getID()]
        if nModule['delNodeNumWidget'].value in nodeids:
            elModule['eset'].deleteEntityWithID(el.getID())
            elModule['eIDWidget'].value = elModule['eset'].getNextID()
            element.updateElementData(elModule['eset'], elemCDS)
            element.updateElementText(elModule['divElements'], elModule['eset'], False, debugInfo)
    #remove the node
    nModule['nset'].deleteEntityWithID(nModule['delNodeNumWidget'].value)
    nModule['delNodeNumWidget'].value = 0
    nModule['nIDWidget'].value = nModule['nset'].getNextID()
    updateCoordData(nModule['nset'], nodeCDS)
    updateNodeText(nModule['divNodes'], nModule['nset'], False, debugInfo)
    bc.deactivateBCModule(bcModule)
    element.deactivateElementModule(elModule)
    nModule['assignDOFsButton'].disabled = False
    solver.checkModelOnClick(nModule, elModule, bcModule, solModule, modeCDS)

def delAllNodesOnClick(nModule, elModule, bcModule, solModule, nodeCDS, elemCDS, ssetCDS, modeCDS, debugInfo):
    clearNodeModule(nModule, nodeCDS, debugInfo)
    bc.clearBCModule(bcModule, ssetCDS, debugInfo)
    bc.deactivateBCModule(bcModule)
    element.clearElementModule(elModule, elemCDS, debugInfo)
    element.deactivateElementModule(elModule)
    solver.checkModelOnClick(nModule, elModule, bcModule, solModule, modeCDS)

def assignDOFsOnClick(nModule, elModule, solModule, debugInfo):
    if nModule['nset'].getSize() >= 2:
        nModule['nset'].assignDOFs()
        updateNodeText(nModule['divNodes'], nModule['nset'], True, debugInfo)
        element.activateElementModule(elModule, debugInfo)
        nModule['assignDOFsButton'].disabled = True
        solModule['solveButton'].disabled = True

def toggleNodeLabels(attr, old, new, labels):
    hide(labels['nodes']) if new else show(labels['nodes'])

def toggleNodeInfo(attr, old, new, nModule):
    show(nModule['divNodes']) if new else hide(nModule['divNodes'])

"""
Node module layout
"""
def createNodeLayout(debug=False):
    nset = NodeSet()
    nIDWidget = NumericInput(value=1, title="Node ID:",mode='int', width=50,height=50)
    nXWidget = NumericInput(value=0, title="x [m]:",mode='float', width=75,height=50)
    nYWidget = NumericInput(value=0, title="y [m]:",mode='float', width=75)
    delNodeNumWidget = NumericInput(value=0, title="Node to be deleted:",mode='int', width=50)
    addNodeButton = Button(label="Add Node", button_type="primary", width=50)
    delNodeButton = Button(label="Remove Node", button_type="warning", width=50)
    assignDOFsButton = Button(label="Continue", button_type="success", width=50)
    delAllNodesButton = Button(label="Remove All Nodes", button_type="danger", width=10)
    nodeLabelsToggle= Toggle(label="Hide Node Numbers", button_type='default', width=150)
    showNodeInfoToggle = Toggle(label="Show Node Info", button_type='default', width=150)
    divNodes = Div(text= '<b>Nodes</b>:<br> <br><p style="color:red"><b>Click Continue when node input ready</b></p>', \
        width=250, height=800, visible=False)

    nodeLayoutDict = {'nset': nset, 'nIDWidget':nIDWidget, 'nXWidget':nXWidget, 'nYWidget':nYWidget, \
        'delNodeNumWidget':delNodeNumWidget, 'addNodeButton':addNodeButton, 'delNodeButton':delNodeButton, \
        'delAllNodesButton':delAllNodesButton, 'assignDOFsButton':assignDOFsButton, 'divNodes':divNodes, \
        'nodeLabelsToggle':nodeLabelsToggle, 'showNodeInfoToggle':showNodeInfoToggle}
    return nodeLayoutDict