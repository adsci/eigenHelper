import numpy as np

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
