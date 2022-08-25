import numpy as np

class NodeSet():
    def __init__(self):
        self.nodes = []

    def __str__(self):
        desc = "<b>Nodes</b>:<br>"
        for node in self.nodes:
            desc += node.__str__() + "<br>"
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


class Node():
    def __init__(self,x,y,id):
        self.coords=[x,y]
        self.id = id

    def __str__(self):
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
