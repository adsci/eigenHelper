from bokeh.models import Div, Button
from utils import *

def printMessage(message, color, divSol):
    divSol.text = f'<br><p style="color:{color}"><b>{message}</b></p>'

def checkDanglingNodes(nset, elset):
    ndofs = []
    for node in nset.members:
        ndofs.append(node.getDOFs())
    n_unique = np.unique(ndofs)
    eldofs = []
    for element in elset.members:
        eldofs.append(element.getEdof())
    e_unique = np.unique(eldofs)
    return np.array_equal(n_unique, e_unique)

def checkStiffnessSingularity(elset, supset):
    eldofs = []
    for element in elset.members:
        eldofs.append(element.getEdof())
    dofs = np.unique(eldofs)
    bc = supset.gatherConstraints()
    free = np.setdiff1d(dofs, bc) - 1
    Kfree = elset.getStiffnessMatrix()[np.ix_(free,free)]
    kRank = np.linalg.matrix_rank(Kfree)
    if kRank < min(Kfree.shape):
        return False
    return True


"""
Solver module callbacks
"""
def checkModelOnClick(nModule, elModule, bcModule, solModule):
    if not nModule['nset'].members:
        solModule['solveButton'].disabled = True
        printMessage("No nodes were defined. Add model nodes and press Continue", "red", solModule['divSolver'])
        return False
    if not elModule['eset'].members:
        solModule['solveButton'].disabled = True
        printMessage("No elements were defined. Add elements and press Continue", "red", solModule['divSolver'])
        return False
    if not checkDanglingNodes(nModule['nset'], elModule['eset']):
        solModule['solveButton'].disabled = True
        printMessage("There are free nodes (not associated with any element). Remove them or add elements.", "red", solModule['divSolver'])
        return False
    if not bcModule['sset'].members:
        solModule['solveButton'].disabled = True
        printMessage("No supports were defined. Add supports and try again", "red", solModule['divSolver'])
        return False
    if not checkStiffnessSingularity(elModule['eset'], bcModule['sset']):
        solModule['solveButton'].disabled = True
        printMessage("Stiffness matrix singular. Check boundary conditions", "red", solModule['divSolver'])
        return False
    printMessage("Model check OK. Click Solve to proceed", "green", solModule['divSolver'])
    solModule['solveButton'].disabled = False
    return True


def solveOnClick(elModule, bcModule, solModule):
    K = elModule['eset'].getStiffnessMatrix()
    M = elModule['eset'].getMassMatrix()
    bc = bcModule['sset'].gatherConstraints()
    evals, evecs = cfc.eigen(K,M,bc)
    solModule['eigenvalues'] = evals
    solModule['eigenvectors'] = evecs
    printMessage(f"Success <br> eigenvalues = {evals}", "green", solModule['divSolver'])

"""
Solver module layout
"""
def createSolverLayout(debug=False):
    checkModelButton = Button(label="Check Model", button_type="success", width=100, disabled=False)
    solveButton = Button(label="Solve", button_type="success", width=100, disabled=True)
    divSolver = Div(text= "", width=350, height=300)

    solverLayoutDict = {'checkModelButton': checkModelButton, 'solveButton':solveButton, 'divSolver':divSolver}
    return solverLayoutDict

