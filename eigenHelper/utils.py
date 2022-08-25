import numpy as np
import calfem.core as cfc

np.set_printoptions(precision=3)

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


class NodeSet():
    def __init__(self):
        self.nodes = []

    def printInfo(self,debug=False):
        desc = "<b>Nodes</b>:<br>"
        for node in self.nodes:
            desc += node.printInfo(debug) + "<br>"
        return desc

    def getNumberOfNodes(self):
        return len(self.nodes)

    def addNode(self,x,y,id):
        fndCoords = self.foundCoords(x,y)
        fndID, _ = self.foundID(id)
        if not (fndCoords or fndID):
            self.nodes.append(Node(x,y,id))
            return True
        return False

    def getNextID(self):
        maxID = np.NINF
        for node in self.nodes:
            if node.getID() > maxID:
                maxID = node.getID()
        return maxID + 1

    def foundCoords(self,x,y):
        for node in self.nodes:
            if (abs(node.getX() - x) <= 1e-6) and (abs(node.getY() - y) < 1e-6):
                return True
        return False

    def foundID(self,id):
        for ind, node in enumerate(self.nodes):
            if node.getID() == id:
                return True, ind
        return False, np.NAN

    def deleteNodeWithID(self,id):
        fnd, ind = self.foundID(id)
        if fnd:
            del self.nodes[ind]

    def getExEy(self):
        xlist = []
        ylist = []
        idlist = []
        for node in self.nodes:
            xlist.append(node.getX())
            ylist.append(node.getY())
            idlist.append(str(node.getID()))
        return (np.array(xlist), np.array(ylist), idlist)

    def assignDOFs(self):
        for i, node in enumerate(self.nodes):
            node.setDOFs(np.array([3*(i+1)-2, 3*(i+1)-1, 3*(i+1)]))

    def getNodeWithID(self, id):
        fnd, ind = self.foundID(id)
        if not fnd:
            return
        return self.nodes[ind]


class Element():
    def __init__(self, id, nodeA, nodeB, prop):
        self.id = id
        self.na = nodeA
        self.nb = nodeB
        self.edof = self.na.getDOFs() + self.nb.getDOFs()
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


class ElementSet():
    def __init__(self):
        self.elements = []

    def printInfo(self,debug=False):
        desc = "<b>Elements</b>:<br>"
        for elem in self.elements:
            desc += elem.printInfo(debug) + "<br><br>"
        return desc

    def getNumberOfElements(self):
        return len(self.elements)

    def addElement(self,id, na, nb, elprop):
        fndNds = self.foundNodes(na,nb)
        fndID, _ = self.foundID(id)
        if not (fndNds or fndID):
            self.elements.append(Element(id,na,nb,elprop))
            return True
        return False

    def getNextID(self):
        maxID = np.NINF
        for elem in self.elements:
            if elem.getID() > maxID:
                maxID = elem.getID()
        return maxID + 1

    def foundNodes(self,n1,n2):
        for elem in self.elements:
            if ((elem.na is n1) and (elem.nb is n2)) or ((elem.na is n2) and (elem.nb is n1)):
                return True
        return False

    def foundID(self,id):
        for ind, elem in enumerate(self.elements):
            if elem.getID() == id:
                return True, ind
        return False, np.NAN

    def deleteElemWithID(self,id):
        fnd, ind = self.foundID(id)
        if fnd:
            del self.elements[ind]

    def getExEy(self):
        ex = np.array([])
        ey = np.array([])
        for elem in self.elements:
            iex, iey = elem.getExEy()
            ex = np.concatenate((ex, iex))
            ey = np.concatenate((ey, iey))
        return ex, ey
