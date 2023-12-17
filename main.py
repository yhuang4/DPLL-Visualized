from input import read_cnf_file
import copy
import argparse

# Start of util funcitons

def assignment_to_string(A, default_true):
    A = A[1:]
    for i in range(len(A)):
        if A[i] == 0:
            A[i] = str(i + 1) if default_true else '_'
        else:
            A[i] = str(A[i] * (i + 1))
    return " ".join(A)

def print_tree(node, depth=0, prefix="|- ", skip=False):
    if not skip:
        if depth == 0:
            print(node.p)
        else:
            print(f"{prefix * depth}{node.p}")

    if node.left:
        print_tree(node.left, depth + 1, prefix)
    if node.right:
        print_tree(node.right, depth + 1, prefix)

class TreeNode:
    def __init__(self, p):
        self.p = p
        self.left = None
        self.right = None

# End of util functions

class State():
    def __init__(self, F, A, implied, p, print):
        self.F = F  # Shared formula, potentially with newly learned clauses
        self.A = copy.deepcopy(A)  # Partial interpretation/assignments
        self.F_A = None  # Status of F interpreted by A. Notice that this may not always be up to date. 
        self.implied = copy.deepcopy(implied)  # Implied assignments in chronological order under this state
        self.print = print
        self.TreeNode = TreeNode(p)

    def eval_helper(self, to_eval):
        # Update F_A based on F or F_A
        new_F_A = []
        for i, clause in to_eval:
            new_clause = []
            for lit in clause:
                if (lit > 0 and self.A[lit] == 1) or (lit < 0 and self.A[-lit] == -1): # lit is true
                    new_clause = None  # Delete a clause if it's satisfied
                    break
                elif self.A[abs(lit)] == 0:  # Not assigned
                    new_clause.append(lit)
            if new_clause != None:
                new_F_A.append((i, new_clause))
        
        self.F_A = new_F_A

    def eval(self):
        if self.F_A == None: 
            self.eval_helper(self.F)
        else:
            self.eval_helper(self.F_A)

    def assign_val(self, p):
        if p > 0:
            self.A[p] = 1
        else:
            self.A[-p] = -1

    def sat(self):
        # Returns true if the formula is satisfied under A
        return len(self.F_A) == 0
    
    def apply_transform(self, p):
        self.assign_val(p)
        self.eval()
    
    def unit_prop(self):
        # Aggressively find unit clauses and set the literals to be true
        units = []
        while True:
            unit_found = False
            for i, clause in self.F_A:
                if len(clause) == 1:
                    unit_found = True
                    units.append(clause[0])
                    self.apply_transform(clause[0])
                    self.implied.append((abs(clause[0]), i))
                    break

            if unit_found: continue
            else: break

        if self.print and len(units):
            print('Unit propagating:       ', ' -> '.join(list(map(str, units))))
            print('Partial interpretation: ', assignment_to_string(self.A, default_true=False))
    
    def get_conflict(self):
        # An empty clause in F_A means there's a conflict
        for i, clause in self.F_A:
            if len(clause) == 0:
                return i
        return None

    def learning_procedure(self, conflict):
        def most_recent_implied(C):
            C = list(map(abs, C))
            for p, i in reversed(self.implied):
                if abs(p) in C:
                    return (p, i)
            
            return (None, None)
        
        def resolve(C, C_pr):
            """
            Example: 
            l = 7          (most recent implied literal)
            C = [-1 -7 -5] (conflict, all false)
            C' = [-1 -6 7] (clause that implied 7, since -1 -6 are false)
            We need C or C', so by binary resolution, we have [-1 -5 -6]
            """
            for lit in C_pr:
                if -lit in C:
                    C.remove(-lit)  # Canceled out by resolution
                elif lit in C:
                    pass
                else:
                    C.append(lit)
        
        C = copy.deepcopy(self.F[conflict][1])
        while True:
            # Loop until all implied literals are replaced by decision literals
            l, i = most_recent_implied(C)
            if l == None:
                return C
            C_pr = self.F[i][1]  # C', the clause that implied l
            resolve(C, C_pr)

    def choose_atom(self):
        # Guaranteed to have non empty formula and no empty clause when called
        # Choose the first literal (unassigned) in F_A
        return abs(self.F_A[0][1][0])  
    

def dpll(state):
    state.unit_prop()
    
    if state.sat():
        return state.A
    
    conflict = state.get_conflict()

    if conflict != None:
        learned_clause = state.learning_procedure(conflict)
        if state.print:
            print('Conflict found:         ', state.F[conflict][1])
            print('Learning clause:        ', learned_clause)
        if len(learned_clause) == 0:
            # An empty clause is learned so the fomula can never be satisfied
            print('UNSAT%')
            exit()
        elif learned_clause != conflict:
            # Add newly learned clause to the shared formula
            # Note that it's in the form (i, clause), which stands for C_i = clause for indexing
            state.F.append((len(state.F), learned_clause))
            
        if state.print: print()
        return None
    else:
        # No conflict. Proceed to assign new values.
        if state.print: print()

        p = state.choose_atom()

        # New state where p is set to true
        p_true = State(state.F, state.A, state.implied, p=p, print=state.print)

        if state.print:
            state.TreeNode.left = p_true.TreeNode
            print(f'Setting {p} to be true')
        p_true.apply_transform(p)
        res_p_true = dpll(p_true)
        if res_p_true != None:
            return res_p_true

        # Setting p to be true failed. Try setting p to be false.
        p_false = State(state.F, state.A, state.implied, p=-p, print=state.print)
        if state.print:
            state.TreeNode.right = p_false.TreeNode
            print(f'Setting {p} to be false')
        p_false.apply_transform(-p)

        res_p_false = dpll(p_false)
        return res_p_false

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--print', action='store_true', help='visualize the decision process')
parser.add_argument('file_path', type=str, help='path to the cnf file')
args = parser.parse_args()

nbvar, nbclauses, F = read_cnf_file(args.file_path)
init_F = copy.deepcopy(F)
F = list(enumerate(F))
A = [0] * (nbvar + 1)
S = State(F, A, [], p=0, print=args.print)
S.eval()

res = dpll(S)
if S.print:
    if res != None: print()
    print('Decision Tree:')
    print_tree(S.TreeNode, skip=True)
    print()
if res != None:
    print('SAT')
    print(assignment_to_string(res, default_true=True) + ' 0%')
else:
    print('UNSAT%')