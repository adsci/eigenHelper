from bokeh.models import Div, Button, Spinner, Slider
from utils import *
import howto

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
    Also returns False if there are no free degrees of freedom.
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
    """
    Builds a multidimensional array with size (n_elements x 6 x n_eigenvectors).
    For each eigenvector and element nodal displacements/rotations
    [u1 v1 phi1 u2 v2 phi2].T
    are reconstructed from the global solution using CALFEM function extract_eldisp.
    """
    disp_extracted = np.zeros((elset.getSize(),6,evecs.shape[1]))
    for i in range(evecs.shape[1]):
        disp_extracted[:,:,i] = cfc.extract_eldisp(elset.getModelEdof(),evecs[:,i])
    return disp_extracted

def computeContinousDisplacement(elset, disp_extracted, sfac=None):
    """
    Builds multidimensional arrays ex_cont, ey_cont with size (n_elements x 21 x n_eigenvectors)
    and computed continuous displacements (in x- and y-directions, respectively)
    at 21 points along the beam element from the global displacements/rotations.
    For each eigenvector and element the corresponding displacements
    [u1 u2 u3 ... u21].T and [v1 v2 v3 ... v21].T
    are computed from element nodal values using CALFEM function beam2crd and put into the corresponding
    column of ex_cont and ey_cont.
    """
    ex, ey = elset.getExEy()
    nel = elset.getSize()
    ex_cont = np.zeros((nel,21,disp_extracted.shape[2]))
    ey_cont = np.zeros((nel,21,disp_extracted.shape[2]))
    dx_max = float(np.max(ex))-float(np.min(ex))
    dy_max = float(np.max(ey))-float(np.min(ey))
    dl_max = max(dx_max, dy_max)
    ed_max = float(np.max(np.max(np.abs(disp_extracted))))
    if not sfac:
        sfac = 1*dl_max/ed_max
    for i in range(disp_extracted.shape[2]):
        ex_cont[:,:,i], ey_cont[:,:,i] = cfc.beam2crd(np.array(ex), np.array(ey), disp_extracted[:,:,i], sfac)
    return ex_cont, ey_cont, sfac

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
    modeCDS[0].data = {'x':[], 'y':[]}
    modeCDS[1].visible = False
    modeCDS[1].text=""

"""
Solver module callbacks
"""
def checkModelOnClick(nModule, elModule, bcModule, solModule, htModule, modeCDS):
    if (not nModule['nset'].members) or (not nModule['assignDOFsButton'].disabled):
        for widget in [solModule['solveButton'], solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
            disableAndHide(widget)
        clearModeCDS(modeCDS)
        printMessage("No nodes were defined or degrees of freedom were not assigned yet. Add model nodes and press Define Elements button", "red", solModule['divSolver'])
        htModule['colors'] = ['black'] + 5*['red']
        howto.updateHowtoDiv(htModule)
        return
    if (not elModule['eset'].members) or (not elModule['assembleButton'].disabled):
        for widget in [solModule['solveButton'], solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
            disableAndHide(widget)
        clearModeCDS(modeCDS)
        printMessage("No elements were defined or global matrices have not been assembled yet. Add elements and press Define Supports button", "red", solModule['divSolver'])
        htModule['colors'] = ['black'] + ['green'] + 4*['red']
        howto.updateHowtoDiv(htModule)
        return
    if not checkDanglingNodes(nModule['nset'], elModule['eset']):
        for widget in [solModule['solveButton'], solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
            disableAndHide(widget)
        clearModeCDS(modeCDS)
        printMessage("There are free nodes (not associated with any element). Remove them or add elements.", "red", solModule['divSolver'])
        htModule['colors'] = ['black'] + 5*['red']
        howto.updateHowtoDiv(htModule)
        return
    if not bcModule['sset'].members:
        for widget in [solModule['solveButton'], solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
            disableAndHide(widget)
        clearModeCDS(modeCDS)
        printMessage("No supports were defined. Add supports and try again", "red", solModule['divSolver'])
        htModule['colors'] = ['black'] + 2*['green'] + 3*['red']
        howto.updateHowtoDiv(htModule)
        return
    if not checkStiffnessSingularity(elModule['eset'], bcModule['sset']):
        for widget in [solModule['solveButton'], solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
            disableAndHide(widget)
        clearModeCDS(modeCDS)
        printMessage("Stiffness matrix singular. Check boundary conditions", "red", solModule['divSolver'])
        htModule['colors'] = ['black'] + 2*['green'] + 3*['red']
        howto.updateHowtoDiv(htModule)
        return
    printMessage("Model check OK. Click Solve to proceed", "green", solModule['divSolver'])
    enableAndShow(solModule['solveButton'])
    htModule['colors'] = ['black'] + 4*['green'] + ['red']
    howto.updateHowtoDiv(htModule)
    for widget in [solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton'] ]:
        disableAndHide(widget)
    clearModeCDS(modeCDS)
    return


def solveOnClick(elModule, bcModule, solModule, htModule, modeCDS):
    K = elModule['eset'].getStiffnessMatrix()
    M = elModule['eset'].getMassMatrix()
    bc = bcModule['sset'].gatherConstraints()
    #solve eigenvalue problem
    ddofs = elModule['eset'].ddofs
    if ddofs.any():
        #dangling nodes need to be removed for the solution
        remainingDofs = np.setdiff1d(np.arange(elModule['eset'].ndof), ddofs - 1)
        Krem = K[np.ix_(remainingDofs,remainingDofs)]
        Mrem = M[np.ix_(remainingDofs, remainingDofs)]
        bcrem = np.copy(bc)
        for dof in ddofs:
            mask = np.where(bc > dof)
            bcrem[mask] -= 1
        evals, evecs = cfc.eigen(Krem,Mrem,bcrem)
        #after solution add zeros where the dangling nodes were to make CALFEM functions work
        for dof in ddofs:
            evecs = np.insert(evecs, dof-1, 0, axis=0)
    else:
        evals, evecs = cfc.eigen(K,M,bc)
    a_extracted = extractEigenvectors(elModule['eset'], evecs)
    exc, eyc, sfac = computeContinousDisplacement(elModule['eset'], a_extracted)
    solution = {'eigenvalues':evals, 'eigenvectors':evecs, 'a_extracted':a_extracted, 'exc':exc, 'eyc':eyc, \
        'sfac':sfac}
    solModule['solution'] = solution
    #show the first eigenmode directly
    updateSolutionData(solModule, modeCDS, eigenmode=1)
    disableAndHide(solModule['solveButton'])
    for widget in [solModule['modeSpinner'], solModule['scaleSlider'], solModule['flipButton']]:
        enableAndShow(widget)
    solModule['modeSpinner'].value = 1
    solModule['modeSpinner'].high = evals.shape[0]
    solModule['scaleSlider'].value = 1
    htModule['colors'][5] = 'green'
    howto.updateHowtoDiv(htModule)

def changeEigenmode(attr, old, new, solModule, modeCDS):
    updateSolutionData(solModule, modeCDS, new)

def changeScale(attr, old, new, elModule, solModule, modeCDS):
    sfac = solModule['solution']['sfac'] * new
    exc, eyc, _ = computeContinousDisplacement(elModule['eset'], solModule['solution']['a_extracted'], \
        sfac)
    solModule['solution']['exc'] = exc
    solModule['solution']['eyc'] = eyc
    updateSolutionData(solModule, modeCDS, solModule['modeSpinner'].value)

def flip(elModule, solModule, modeCDS):
    solModule['solution']['eigenvectors'] = np.negative(solModule['solution']['eigenvectors'])
    a_extracted = extractEigenvectors(elModule['eset'], solModule['solution']['eigenvectors'])
    sfac = solModule['solution']['sfac'] * solModule['scaleSlider'].value
    exc, eyc, _ = computeContinousDisplacement(elModule['eset'], a_extracted, sfac)
    solModule['solution']['a_extracted'] = a_extracted
    solModule['solution']['exc'] = exc
    solModule['solution']['eyc'] = eyc
    updateSolutionData(solModule, modeCDS, solModule['modeSpinner'].value)


"""
Solver module layout
"""
def createSolverLayout(debug=False):
    checkModelButton = Button(label="Check Model", button_type="success", width=100, disabled=False)
    solveButton = Button(label="Solve", button_type="success", width=100, disabled=True, visible=False)
    modeSpinner = Spinner(title="Eigenvalue", low=1, high=10, step=1, value=1, mode='int', width=75, visible=False, disabled=True)
    scaleSlider = Slider(start=0.01, end=3, value=1, step=0.01, title="Scale", disabled=True, visible=False, show_value=False)
    flipButton = Button(label="Flip", button_type="default", width=75, disabled=True, visible=False)
    divSolver = Div(text= "", width=350, height=300)
    solution = {}

    solverLayoutDict = {'checkModelButton': checkModelButton, 'solveButton':solveButton, \
        'modeSpinner':modeSpinner,  'scaleSlider':scaleSlider, 'flipButton':flipButton, \
        'divSolver':divSolver, 'solution':solution}
    return solverLayoutDict

