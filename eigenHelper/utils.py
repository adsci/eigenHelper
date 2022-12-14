import numpy as np
import calfem.core as cfc

np.set_printoptions(precision=3)

class EntitySet():
    def __init__(self):
        self.members=[]

    def printInfo(self, debug=False):
        desc = []
        for member in self.members:
            desc.append(member.printInfo(debug) + "<br>")
        return desc

    def clear(self):
        self.members=[]

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

def disableAndHide(widget):
    widget.visible = False
    widget.disabled = True

def enableAndShow(widget):
    widget.visible = True
    widget.disabled = False

def show(div):
    div.visible = True

def hide(div):
    div.visible = False