from bokeh.models import Div, RadioButtonGroup, NumericInput, Button
from utils import *

class Support():
    def __init__(self, typeID, node):
        self.type = typeID
        self.node = node

    def getType(self):
        types = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
        return types[self.type]

    def getNode(self):
        return self.node

    def printInfo(self, debug=False):
        if debug:
            return "Support " +str(self.getType()) + " at Node " + str(self.getNode().getID()) +". Locked local dofs " + str(self.getConstrainedDOFs())
        else:
            return "Support " +str(self.getType()) + " at Node " + str(self.getNode().getID())

    def getConstrainedDOFs(self):
        locked = [ [0,1,2], [1,2], [0,2], [0,1], [1], [0]]
        return locked[self.type]

    def typeToMarker(self, typeName):
        if typeName == 'S1':
            return 'square'
        elif typeName == 'S2' or typeName == 'S3':
            return 'square_pin'
        elif typeName == 'S4':
            return 'triangle'
        elif typeName == 'S5' or typeName == 'S6':
            return 'triangle_pin'
        return 'hex'


class SupportSet(EntitySet):
    def foundAtNode(self, nid):
        for ind, support in enumerate(self.members):
            if support.getNode().getID() == nid:
                return True, ind
        return False, np.NAN

    def deleteAtNode(self, nid):
        fnd, ind = self.foundAtNode(nid)
        if fnd:
            del self.members[ind]

    def getExEy(self):
        xlist = []
        ylist = []
        typelist = []
        markertypes = []
        for support in self.members:
            xlist.append(support.getNode().getX())
            ylist.append(support.getNode().getY())
            typelist.append(support.getType())
            markertypes.append(support.typeToMarker(support.getType()))
        return (np.array(xlist), np.array(ylist), typelist, markertypes)

    def gatherConstraints(self):
        constraints = np.array([], dtype=np.intc)
        for support in self.members:
            constraints = np.concatenate( (constraints, support.getNode().getDOFs()[np.ix_(support.getConstrainedDOFs())]) )
        return constraints

def createSupport(nset, type, node):
    fnd, _ = nset.foundID(node.getID())
    if not fnd:
        return False
    newSupport = Support(type, node)
    return newSupport

def activateSupportImg(choice):
    padding = ['&emsp;', '&emsp;', '&emsp; &nbsp', '&emsp;', '&emsp;', '&emsp;']
    newText = '&nbsp &nbsp'
    for i in range(6):
        if i == choice:
            newText += f'<img src="/eigenHelper/static/support{i}.png"> {padding[i]}'
        else:
            newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def deactivateSupportImg():
    padding = ['&emsp;', '&emsp;', '&emsp; &nbsp', '&emsp;', '&emsp;', '&emsp;']
    newText = '&nbsp &nbsp'
    for i in range(6):
        newText += f'<img src="/eigenHelper/static/support{i}.png" style="opacity:0.4;filter:alpha(opacity=40);"> {padding[i]}'
    return newText

def activateBCModule(bcModule):
    for _, val in bcModule.items():
        val.disabled = False
    bcModule['rbgDiv'].text = activateSupportImg(0)

def deactivateBCModule(bcModule):
    for _, val in bcModule.items():
        val.disabled = True
    bcModule['rbgDiv'].text = deactivateSupportImg()

def updateSupportData(supportSet, ssetCDS):
    ex, ey, ids, markers = supportSet.getExEy()
    ssetCDS.data = {'x':ex, 'y':ey, 'types':ids, 'mtype':markers}

def updateSupportText(divText, supset, readyFlag, debugInfo):
    newText = ['<b>Supports</b>:<br>']
    newText += supset.printInfo(debugInfo)
    if not readyFlag:
        newText.append('<br><p style="color:red"><b>Click Check Model when support input ready</b></p>')
    else:
        newText.append('<br><p style="color:green"><b>Ready for check</b></p>')
    divText.text = ''.join(newText)


"""
Boundary Conditions module callbacks
"""
def changeActiveBC(newChoice, bcModule):
    bcModule['rbgDiv'].text = activateSupportImg(newChoice)

def addSupportOnClick(nModule, bcModule, solModule, ssetCDS, debugInfo):
    if not nModule['nset'].foundID(bcModule['addToNodeWidget'].value)[0]:
        return
    # #check whether the support can be added
    for support in bcModule['sset'].members:
        if support.getNode().getID() == bcModule['addToNodeWidget'].value:
            return
    nSupport = createSupport(nModule['nset'], bcModule['rbg'].active, nModule['nset'].getEntityWithID(bcModule['addToNodeWidget'].value))
    if not nSupport:
        return
    bcModule['sset'].add(nSupport)
    bcModule['addToNodeWidget'].value = 0
    updateSupportData(bcModule['sset'], ssetCDS)
    updateSupportText(bcModule['divSupports'], bcModule['sset'], False, debugInfo)
    solModule['solveButton'].disabled = True

def delSupportOnClick(bcModule, solModule, ssetCDS, debugInfo):
    if (not bcModule['sset'].members) or (not bcModule['sset'].foundAtNode(bcModule['deleteFromNodeWidget'].value)[0]):
        return
    bcModule['sset'].deleteAtNode(bcModule['deleteFromNodeWidget'].value)
    bcModule['deleteFromNodeWidget'].value = 0
    bcModule['addToNodeWidget'].value = 0
    updateSupportData(bcModule['sset'], ssetCDS)
    updateSupportText(bcModule['divSupports'], bcModule['sset'], False, debugInfo)
    solModule['solveButton'].disabled = True

def delAllSupportsOnClick(bcModule, solModule, ssetCDS, debugInfo):
    bcModule['sset'].clear()
    bcModule['addToNodeWidget'].value = 0
    updateSupportData(bcModule['sset'], ssetCDS)
    updateSupportText(bcModule['divSupports'], bcModule['sset'], False, debugInfo)
    solModule['solveButton'].disabled = True


"""
Boundary Conditions module layout
"""
def createBCLayout(debug=False):
    sset = SupportSet()
    rbg = RadioButtonGroup(labels=['S1', 'S2', 'S3', 'S4', 'S5', 'S6'], active=0, disabled=True)
    addToNodeWidget = NumericInput(value=0, title="Add support at node:",mode='int', width=50,height=50, disabled=True)
    addSupportButton = Button(label="Add Support", button_type="primary", width=50, disabled=True)
    deleteFromNodeWidget = NumericInput(value=0, title="Remove support at node:",mode='int', width=50,height=50, disabled=True)
    deleteSupportButton = Button(label="Remove Support", button_type="warning", width=50, disabled=True)
    deleteAllSupportsButton = Button(label="Remove All Supports", button_type="danger", width=50, disabled=True)
    rbgText = deactivateSupportImg()
    rbgDiv = Div(text=rbgText, width=400, height=50)
    divSupports = Div(text= "<b>Supports</b>:<br>", width=350, height=300)

    bcLayoutDict = {'sset':sset, 'rbg':rbg, 'addToNodeWidget':addToNodeWidget, 'addSupportButton':addSupportButton, \
        'deleteFromNodeWidget':deleteFromNodeWidget, 'deleteSupportButton':deleteSupportButton, \
        'deleteAllSupportsButton':deleteAllSupportsButton, 'rbgDiv':rbgDiv, 'divSupports':divSupports}
    return bcLayoutDict