from bokeh.models import Div, Button, Spinner
from utils import *

def printMessage(message, color, divSol):
    divSol.text = f'<br><p style="color:{color}"><b>{message}</b></p>'

def checkDanglingNodes(nset, elset):
    """
    Returns True if there are no dangling nodes, False otherwise
    """
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
    """
    Returns True if the stiffness matrix is not singular, False otherwise
    """
    eldofs = []
    for element in elset.members:
        eldofs.append(element.getEdof())
    dofs = np.unique(eldofs)
    bc = supset.gatherConstraints()
    free = np.setdiff1d(dofs, bc) - 1
    if not free.any():
        return False
    Kfree = elset.getStiffnessMatrix()[np.ix_(free,free)]
    kRank = np.linalg.matrix_rank(Kfree)
    if kRank < min(Kfree.shape):
        return False
    return True

def extractEigenvectors(elset, evecs):
    disp_extracted = np.zeros((elset.getSize(),6,evecs.shape[1]))
    for i in range(evecs.shape[1]):
        disp_extracted[:,:,i] = cfc.extract_eldisp(elset.getModelEdof(),evecs[:,i])
    return disp_extracted

def computeContinousDisplacement(elset, disp_extracted):
    ex, ey = elset.getExEy()
    nel = elset.getSize()
    ex_cont = np.zeros((nel,21,disp_extracted.shape[2]))
    ey_cont = np.zeros((nel,21,disp_extracted.shape[2]))
    dx_max = float(np.max(ex))-float(np.min(ex))
    dy_max = float(np.max(ey))-float(np.min(ey))
    dl_max = max(dx_max, dy_max)
    ed_max = float(np.max(np.max(np.abs(disp_extracted))))
    sfac = 0.1*dl_max/ed_max
    for i in range(disp_extracted.shape[2]):
        ex_cont[:,:,i], ey_cont[:,:,i] = cfc.beam2crd(np.array(ex), np.array(ey), disp_extracted[:,:,i], 0.5)
    return ex_cont, ey_cont

def updateSolutionData(solModule, modeCDS, eigenmode):
    exc = solModule['solution']['exc']
    eyc = solModule['solution']['eyc']
    nel = exc.shape[0]
    exclist, eyclist = [], []
    for i in range(nel):
        exclist.append(exc[i,:,eigenmode-1])
        eyclist.append(eyc[i,:,eigenmode-1])
    modeCDS[0].data = {'x':exclist, 'y':eyclist}
    modeCDS[1].visible = True
    modeCDS[1].text=f"f = {np.sqrt(solModule['solution']['eigenvalues'][eigenmode-1])/(2*np.pi):.2f} Hz"

def clearModeCDS(modeCDS):
    modeCDS[0].data = {}
    modeCDS[1].visible = False
    modeCDS[1].text=""

"""
Solver module callbacks
"""
def checkModelOnClick(nModule, elModule, bcModule, solModule, modeCDS):
    if not nModule['nset'].members:
        disableAndHide(solModule['solveButton'])
        disableAndHide(solModule['modeSpinner'])
        clearModeCDS(modeCDS)
        printMessage("No nodes were defined. Add model nodes and press Continue", "red", solModule['divSolver'])
        return
    if not elModule['eset'].members:
        disableAndHide(solModule['solveButton'])
        disableAndHide(solModule['modeSpinner'])
        clearModeCDS(modeCDS)
        printMessage("No elements were defined. Add elements and press Continue", "red", solModule['divSolver'])
        return
    if not checkDanglingNodes(nModule['nset'], elModule['eset']):
        disableAndHide(solModule['solveButton'])
        disableAndHide(solModule['modeSpinner'])
        clearModeCDS(modeCDS)
        printMessage("There are free nodes (not associated with any element). Remove them or add elements.", "red", solModule['divSolver'])
        return
    if not bcModule['sset'].members:
        disableAndHide(solModule['solveButton'])
        disableAndHide(solModule['modeSpinner'])
        clearModeCDS(modeCDS)
        printMessage("No supports were defined. Add supports and try again", "red", solModule['divSolver'])
        return
    if not checkStiffnessSingularity(elModule['eset'], bcModule['sset']):
        disableAndHide(solModule['solveButton'])
        disableAndHide(solModule['modeSpinner'])
        clearModeCDS(modeCDS)
        printMessage("Stiffness matrix singular. Check boundary conditions", "red", solModule['divSolver'])
        return
    printMessage("Model check OK. Click Solve to proceed", "green", solModule['divSolver'])
    enableAndShow(solModule['solveButton'])
    disableAndHide(solModule['modeSpinner'])
    clearModeCDS(modeCDS)
    return


def solveOnClick(elModule, bcModule, solModule, modeCDS):
    K = elModule['eset'].getStiffnessMatrix()
    M = elModule['eset'].getMassMatrix()
    bc = bcModule['sset'].gatherConstraints()
    evals, evecs = cfc.eigen(K,M,bc)
    a_extracted = extractEigenvectors(elModule['eset'], evecs)
    exc, eyc = computeContinousDisplacement(elModule['eset'], a_extracted)
    solution = {'eigenvalues':evals, 'eigenvectors':evecs, 'a_extracted':a_extracted, 'exc':exc, 'eyc':eyc}
    solModule['solution'] = solution
    #show the first eigenmode directly
    updateSolutionData(solModule, modeCDS, eigenmode=1)
    disableAndHide(solModule['solveButton'])
    enableAndShow(solModule['modeSpinner'])
    solModule['modeSpinner'].value = 1
    solModule['modeSpinner'].high = evals.shape[0]

def changeEigenmode(attr, old, new, solModule, modeCDS):
    updateSolutionData(solModule, modeCDS, new)
    # modeCDS[1].visible = True
    # modeCDS[1].text=f"f = {np.sqrt(solModule['solution']['eigenvalues'][new-1])/(2*np.pi):.2f} Hz"

"""
Solver module layout
"""
def createSolverLayout(debug=False):
    checkModelButton = Button(label="Check Model", button_type="success", width=100, disabled=False)
    solveButton = Button(label="Solve", button_type="success", width=100, disabled=True, visible=False)
    modeSpinner = Spinner(title="Eigenmode associated with eigenvalue", low=1, high=10, step=1, value=1, mode='int', width=100, visible=False, disabled=True)
    divSolver = Div(text= "", width=350, height=300)
    solution = {}

    solverLayoutDict = {'checkModelButton': checkModelButton, 'solveButton':solveButton, \
        'modeSpinner':modeSpinner, 'divSolver':divSolver, 'solution':solution}
    return solverLayoutDict

