"""
Node module with helper function and classes
"""
from bokeh.models import Div, NumericInput, Button
from utils import *
from element import activateElementModule, deactivateElementModule

class Node():
    def __init__(self,x,y,id):
        self.coords=[x,y]
        self.id = id
        self.dofs = []

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

    def setID(self,newID):
        self.id = newID

    def getDOFs(self):
        return self.dofs

    def setDOFs(self,dofArray):
        self.dofs = dofArray

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
            node.setDOFs(np.array([3*(i+1)-2, 3*(i+1)-1, 3*(i+1)]))


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

def updateNodeText(divText, nodeset, debugInfo):
    divText.text = "<b>Nodes</b>:<br>"  + nodeset.printInfo(debugInfo)


"""
Node module callbacks
"""
def addNodeOnClick(nodeset, nxWidget, nyWidget, nidInput, dtext, nodeCDS, debugInfo):
    if nidInput.value <= 0:
        return
    #check whether the node can be added
    nNode = createNode(nodeset, float(nxWidget.value), float(nyWidget.value), nidInput.value)
    if not nNode:
        return
    nodeset.add(nNode)
    nidInput.value = nodeset.getNextID()
    updateCoordData(nodeset, nodeCDS)
    updateNodeText(dtext, nodeset, debugInfo)
    dtext.text += '<br><p style="color:red"><b>Assign DOFs when node input ready</b></p>'

def delNodeOnClick(nodeset, elModule, nidWidget, delNodeWidget, dtext, nodeCDS, debugInfo):
    if (not nodeset.members) or (not nodeset.foundID(delNodeWidget.value)[0]):
        return
    nodeset.deleteEntityWithID(delNodeWidget.value)
    delNodeWidget.value = 0
    nidWidget.value = nodeset.getNextID()
    updateCoordData(nodeset, nodeCDS)
    updateNodeText(dtext, nodeset, debugInfo)
    deactivateElementModule(elModule)
    dtext.text += '<br><p style="color:red"><b>Assign DOFs when node input ready</b></p>'

def delAllNodesOnClick(nodeset, elModule, nidWidget, dtext, nodeCDS, debugInfo):
    nodeset.clear()
    nidWidget.value = nodeset.getNextID()
    updateCoordData(nodeset, nodeCDS)
    updateNodeText(dtext, nodeset, debugInfo)
    deactivateElementModule(elModule)
    dtext.text += '<br><p style="color:red"><b>Assign DOFs when node input ready</b></p>'

def assignDOFsOnClick(nodeset, elModule, dtext, debugInfo):
    if nodeset.members:
        nodeset.assignDOFs()
        updateNodeText(dtext, nodeset, debugInfo)
        activateElementModule(elModule)
        dtext.text += '<br><p style="color:green"><b>DOFs assigned, ready for element input</b></p>'


"""
Node module layout
"""
def createNodeLayout(debug=False):
    nset = NodeSet()
    nIDWidget = NumericInput(value=1, title="Node ID:",mode='int', width=50,height=50)
    nXWidget = NumericInput(value=0, title="x [m]:",mode='float', width=75,height=50)
    nYWidget = NumericInput(value=0, title="y [m]:",mode='float', width=75)
    delNodeNumWidget = NumericInput(value=0, title="Node to be deleted:",mode='int', width=50)
    addNodeButton = Button(label="Add Node", button_type="primary", width=50 )
    delNodeButton = Button(label="Delete Node", button_type="warning", width=50 )
    assignDOFsButton = Button(label="Assign DOFs", button_type="success", width=50 )
    delAllNodesButton = Button(label="Delete All Nodes", button_type="danger", width=100 )
    divNodes = Div(text= '<b>Nodes</b>:<br> <br><p style="color:red"><b>Assign DOFs when node input ready</b></p>', width=250, height=300)

    nodeLayoutDict = {'nset': nset, 'nIDWidget':nIDWidget, 'nXWidget':nXWidget, 'nYWidget':nYWidget, \
        'delNodeNumWidget':delNodeNumWidget, 'addNodeButton':addNodeButton, 'delNodeButton':delNodeButton, \
        'delAllNodesButton':delAllNodesButton, 'assignDOFsButton':assignDOFsButton, 'divNodes':divNodes}
    return nodeLayoutDict