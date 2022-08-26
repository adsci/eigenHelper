import numpy as np
import calfem.core as cfc

np.set_printoptions(precision=3)


class EntitySet():
    def __init__(self):
        self.members=[]

    def printInfo(self, debug=False):
        desc = ''
        for member in self.members:
            desc += member.printInfo(debug) + "<br>"
        return desc

    def add(self, newEntity):
        self.members.append(newEntity)

    def getSize(self):
        return len(self.members)

    def getNextID(self):
        maxID = np.NINF
        for member in self.members:
            if member.getID() > maxID:
                maxID = member.getID()
        if maxID == np.NINF:
            maxID = 0
        return maxID + 1

    def foundID(self,id):
        for ind, member in enumerate(self.members):
            if member.getID() == id:
                return True, ind
        return False, np.NAN

    def deleteEntityWithID(self,id):
        fnd, ind = self.foundID(id)
        if fnd:
            del self.members[ind]

    def getEntityWithID(self,id):
        fnd, ind = self.foundID(id)
        if not fnd:
            return False
        return self.members[ind]


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
            return info
        else:
            info = f"Element with nodes {str(self.getNodes())}\n"
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



def createNode(nodeset, x, y, id):
    fndCoords = nodeset.foundCoords(x,y)
    fndID, _ = nodeset.foundID(id)
    if not (fndCoords or fndID):
        newNode = Node(x,y,id)
        return newNode
    return False

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