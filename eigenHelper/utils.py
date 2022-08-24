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

    def addNode(self,x,y):
        if not self.found(x,y):
            self.nodes.append(Node(x,y,self.getNextID()))

    def getNextID(self):
        return len(self.nodes) + 1

    def found(self,x,y):
        for node in self.nodes:
            if (abs(node.getX() - x) <= 1e-6) and (abs(node.getY() - y) < 1e-6):
                return True
        return False

    def renumber(self,fromID):
        for node in self.nodes:
            if node.getID() <= fromID:
                continue
            else:
                node.setID(node.getID()-1)

    def deleteNodeWithID(self,id):
        assert self.nodes[id-1].getID() == id
        del self.nodes[id-1]
        self.renumber(id)

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
