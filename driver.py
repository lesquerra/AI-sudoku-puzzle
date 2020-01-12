import sys
import queue
from copy import deepcopy

rows = "ABCDEFGHI"
cols = "123456789"

# CSP
class CSP:
    """ Constraint satisfaction problem class """
    def __init__ (self, grid, domain = cols):
        """ Initialize variables, values and constraints """
        self.variables = cross(rows, cols)
        self.values = set_values(grid)		
        
        self.contraint_sets = ([cross(rows, c) for c in cols] +
            			       [cross(r, cols) for r in rows] +
            			       [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])

        self.sets = dict((s, [u for u in self.contraint_sets if s in u]) for s in cross(rows, cols))
        self.neighbors = dict((s, set(sum(self.sets[s],[]))-set([s])) for s in cross(rows, cols))
        self.constraints = {(v, n) for v in self.variables for n in self.neighbors[v]}     


# AUXILIARY FUNCTIONS
def cross(X, Y):
    """ Get all combinations across values of X and Y
    
    Args:
        X: String or character vector input whose values are to be combined with Y
        Y: String or character vector input whose values are to be combined with X
        
    Returns: Returns a list with all possible combinations of X and Y
    
    """
    return [x + y for x in X for y in Y]

def select_next_var(assignment, csp):
    """ Select next field to be assigned through MRV (Minimum Remaining Values)
    
    Args:
        assignment: Dictionary containing fields and values assigned
        csp: CSP class object with current state of the sudoku puzzle board
        
    Returns: Field with fewest legal values remaining in its domain
    
    """
    unassigned_vars = dict((sqr, len(csp.values[sqr])) for sqr in csp.values if sqr not in assignment.keys())
    mrv = min(unassigned_vars, key=unassigned_vars.get)
    return mrv

def forward_check(csp, x, Xi):
    """ Track remaining legal values for unassigned variables
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        x: Current value evaluated at field Xi
        Xi: Current field id (row + column combination)
        
    Returns: No specific return value. Updates remaining legal values for unassigned variables in the CSP class object
    
    """
    csp.values[Xi] = x
    for neighbor in csp.neighbors[Xi]:
        csp.values[neighbor] = csp.values[neighbor].replace(x, '')
       

def set_values(grid):
    """ Set all possible values in cells
    
    Args:
        grid: Single line of text string representing the sudoku puzzle board
        
    Returns: Returns a dictionary with the set of possible values for each cell
    
    """
    i = 0
    values = dict()
    variables = cross(rows, cols)
    for v in variables:
        if grid[i] != "0":
            values[v] = grid[i]
        else:
            values[v] = cols
        i += 1
    return values

def AC_constraint_check(csp, x, Xi, Xj):
    """ Check if all AC constraints are satisfied
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        x: Current value evaluated at field Xi
        Xi: Current field id (row + column combination)
        Xj: Selected neighbor's field id (row + column combination)
        
    Returns: Boolean whether all AC contraints are satisfied (satisfied = True; constraint violation = False)
    
    """
    for neighbor in csp.values[Xj]:
        if Xj in csp.neighbors[Xi] and neighbor != x:
            return False
    return True

def BT_constraint_check(csp, x, Xi, assignment):
    """ Check if all BT constraints are satisfied
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        x: Current value evaluated at field Xi 
        Xi: Current field id (row + column combination)
        assignment: Dictionary containing fields and values assigned
        
    Returns: Boolean whether all BT contraints are satisfied (satisfied = True; constraint violation = False)
    
    """
    for neighbor in csp.neighbors[Xi]:
        if neighbor in assignment.keys():
            if assignment[neighbor] == x:
                return False
    return True

def completed(assignment):
    """ Check if sudoku is full
    
    Args:
        assignment: Dictionary containing fields and values assigned
        
    Returns: Boolean whether current state of the sudoku puzzle board is complete (complete = True; incomplete = False)
    
    """
    return set(assignment.keys())==set(cross(rows, cols))

def solved(csp):
    """ Check if sudoku solved
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        
    Returns: Boolean whether the sudoku puzzle has been successfully completed (yes = True; no = False)
    
    """
    for c in cross(rows, cols):
        if len(csp.values[c])>1:
            return False
    return True

def write(values):
    """ Transform values to string
    
    Args:
        values: CSP values dictionary object 
        
    Returns: Returns a single line of text string representing solved sudoku puzzle board
    
    """
    output = ""
    for c in cross(rows, cols):
        output = output + values[c]
    return output


# AC3 ALGORITHM
def AC3(csp):
    """ AC3 algorithm
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        
    Returns: Boolean if the sudoku puzzle was successfully completed using the AC3 algorithm (yes = True; no = False)
    
    """
    q = queue.Queue()
    for arc in csp.constraints:
        q.put(arc)
    while not q.empty():
        Xi, Xj = q.get()
        if revise(csp, Xi, Xj):
            if len(csp.values[Xi]) == 0:
                return False
            for Xk in (csp.neighbors[Xi] - set(Xj)):
                q.put((Xk, Xi))
    return True 

def revise(csp, Xi, Xj):
    """ Run AC3 constraints check
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        Xi: Current field id (row + column combination)
        Xj: Selected neighbor's field id (row + column combination)
        
    Returns: Boolean whether AC3 constaints check has been completed (yes = True; no = False)
    
    """
    revised = False
    values = set(csp.values[Xi])
    for x in values:
        if AC_constraint_check(csp, x, Xi, Xj):
            csp.values[Xi] = csp.values[Xi].replace(x, "")
            revised = True 
    return revised 


# BTS ALGORITHM
def BTS(csp):
    """ Backtracking Search algorithm
    
    Args:
        csp: CSP class object with current state of the sudoku puzzle board
        
    Returns: Boolean if the sudoku puzzle was successfully completed using the BTS algorithm (yes = True), string if failed ("fail")
    
    """
    return backtrack({}, csp)

def backtrack(assignment, csp):
    """ Run BTS constraints check
    
    Args:
        assignment: Dictionary containing fields and values assigned
        csp: CSP class object with current state of the sudoku puzzle board
        
    Returns: Boolean if the sudoku puzzle was successfully completed using the BTS algorithm (yes = True), string if failed ("fail")
    
    """
    if completed(assignment): return True
    Xi = select_next_var(assignment, csp)
    domain = deepcopy(csp.values)
    for x in csp.values[Xi]:
        if BT_constraint_check(csp, x, Xi, assignment):
            assignment[Xi] = x
            forward_check(csp, x, Xi)
            res = backtrack(assignment, csp)
            if res !="fail":
                return res    
            del assignment[Xi]
            csp.values.update(domain)
    return "fail"


# SUDOKU SOLVER
def solver(given_sudoku_board):
    """ Sudoku solver
    
    Args:
        given_sudoku_board: Input single line of text string representing the given unsolved sudoku puzzle board (0 = empty field)
        
    Returns: Solved sudoku string and used algorithm
    
    """
    AC3(given_sudoku_board)
    if (solved(given_sudoku_board)):
        res = write(given_sudoku_board.values) + " AC3"
    else:
        BTS(given_sudoku_board)
        res = write(given_sudoku_board.values) + " BTS"
    
    return res

if __name__ == "__main__":
    
    # Read the given Sudoku Board
    grid = sys.argv[1]
    
    # Initialize given Sudoku Board as class CSP
    given_sudoku_board = CSP(grid)

    # Run Sudoku Solver
    result = solver(given_sudoku_board)
    
    # Write resulting solved Sudoku Board to file
    f = open("output.txt", "w")
    print(result, file = f)
    f.close()