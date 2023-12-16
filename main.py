from input import read_cnf_file
import copy
import sys

class State():
    def __init__(self, F, A, implied):
        self.F = F
        self.A = copy.deepcopy(A)
        self.F_A = None
        self.implied = copy.deepcopy(implied)

    def eval_helper(self, to_eval):
        new_F_A = []
        for i, clause in to_eval:
            new_clause = []
            for lit in clause:
                if (lit > 0 and self.A[lit] == 1) or (lit < 0 and self.A[-lit] == -1): # lit is true
                    new_clause = None
                    break
                elif self.A[abs(lit)] == 0:  # not assigned
                    new_clause.append(lit)
            if new_clause != None:
                new_F_A.append((i, new_clause))
        
        self.F_A = new_F_A

    def force_eval(self):
        self.eval_helper(self.F)

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
        return len(self.F_A) == 0
    
    def apply_transform(self, p):
        self.assign_val(p)
        self.eval()
    
    def unit_prop(self):
        while True:
            unit_found = False
            for i, clause in self.F_A:
                if len(clause) == 1:
                    unit_found = True
                    self.apply_transform(clause[0])
                    self.implied.append((abs(clause[0]), i))
                    break

            if unit_found: continue
            else: break
    

    def get_conflict(self):
        for i, clause in self.F_A:
            if len(clause) == 0:
                return i
        return None

    def learning_procedure(self, conflict):
        def most_recent_implied(C):
            for p, i in reversed(self.implied):
                if abs(p) in C:
                    return (p, i)
            
            return (None, None)
        
        def resolve(C, C_pr, l):
            for lit in C_pr:
                if -lit in C:
                    C.remove(-lit)  # Canceled out by resolution
                elif lit in C:
                    pass
                else:
                    C.append(lit)
            
        C = copy.deepcopy(self.F[conflict][1])
        while True:  # Loop until all implied literals are replaced
            l, i = most_recent_implied(C)
            if l == None:
                return C
            C_pr = self.F[i][1]  # C'
            resolve(C, C_pr, l)

    def choose_atom(self):
        # Guaranteed to have non empty formula and no empty clause when called
        return abs(self.F_A[0][1][0])  
    

def dpll(state):
    state.unit_prop()
    
    if state.sat():
        return state.A
    
    conflict = state.get_conflict()

    if conflict != None:
        learned_clause = state.learning_procedure(conflict)
        if len(learned_clause) == 0:
            print('UNSAT%')
            exit()
        elif learned_clause != conflict:
            state.F.append((len(state.F), learned_clause))
        return None
    else:
        p = state.choose_atom()
        p_true = State(state.F, state.A, state.implied)

        p_true.apply_transform(p)
        res_p_true = dpll(p_true)
        if res_p_true != None:
            return res_p_true

        p_false = State(state.F, state.A, state.implied)
        p_false.apply_transform(-p)

        res_p_false = dpll(p_false)
        return res_p_false
    
file_path = sys.argv[1]
nbvar, nbclauses, F = read_cnf_file(file_path)
init_F = copy.deepcopy(F)
F = list(enumerate(F))
A = [0] * (nbvar + 1)
S = State(F, A, [])
S.eval()

res = dpll(S)
if res != None:
    res = res[1:]
    for i in range(len(res)):
        if res[i] == 0:
            res[i] = str(i + 1)
        else:
            res[i] = str(res[i] * (i + 1))
    print('SAT')
    print(" ".join(res) + ' 0%')
else:
    print('UNSAT%')