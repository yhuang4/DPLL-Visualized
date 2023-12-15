# while True:
#     sat_input = input().split()
#     if len(sat_input) == 4 and sat_input[0] == 'p' and sat_input[1] == 'cnf':
#         try:
#             nbvar, nbclauses = int(sat_input[2]), int(sat_input[3])
#             break
#         except:
#             pass
#     print('Fomat error. Format: p cnf [nbvar] [nbclauses]')
from input import read_cnf_file
import copy
nbvar, nbclauses = map(int, input().split())

F = []
A = [-1] * (nbvar + 1)
for i in range(nbclauses):
    clause = list(map(int, input().split()))[:-1]
    # clause = list(map(int, input().split()))[:-1]  # Terminated by a 0
    F.append(clause)

# nbvar, nbclauses, F = read_cnf_file('cnfs/uf20-01.cnf')
# A = [-1] * (nbvar + 1)

assignments = []
implied = {}

def get_unit():
    for i, clause in enumerate(F):
        unassigned_count = 0
        unassigned = 0
        unsat = True
        for lit in clause:
            # If the clause is satisfied, break
            if lit > 0 and A[lit] == 1:
                unsat = False
                break
            elif lit < 0 and A[abs(lit)] == 0:
                unsat = False
                break
            
            # Start checking for unassigned
            if A[abs(lit)] == -1:
                unassigned_count += 1
                if unassigned_count > 1:
                    break
                unassigned = lit
        if unsat and unassigned_count == 1:
            implied[abs(unassigned)] = i
            return unassigned
    return 0


def all_sat():
    for clause in F:
        sat = False
        for lit in clause:
            if lit > 0 and A[lit] == 1:
                sat = True
                break
            if lit < 0 and A[abs(lit)] == 0:
                sat = True
                break
        if not sat:
            return False
    return True

def get_conflict():
    for clause in F:
        if len(clause) == 0: continue # improve logic
        no_conflict = False
        for lit in clause:
            if lit > 0 and A[lit] != 0:
                no_conflict = True
                break
            if lit < 0 and A[abs(lit)] != 1:
                no_conflict = True
                break
        if not no_conflict:
            return clause
    return None

def learning_procedure(C):
    C = copy.deepcopy(C)
    C.sort(key=lambda x: abs(x), reverse=True)
    def get_implied():
        for lit in C:
            if abs(lit) in implied:
                return lit
        return 0
    
    def resolve(C_prime, l):
        C.remove(l)
        for lit in C_prime:
            if abs(lit) != abs(l):
                if -lit in C:
                    C.remove(-lit)
                if lit not in C:
                    C.append(lit)
    
    l = get_implied()
    while l != 0:
        C_prime = F[implied[abs(l)]]
        resolve(C_prime, l)
        l = get_implied()
    print('learned', C)
    F.append(C)
    return C


def unit_prop():
    unit = get_unit()
    propped_unit = []
    while unit != 0:
        if unit > 0:
            A[unit] = 1
        else:
            A[abs(unit)] = 0
        assignments.append(unit)
        propped_unit.append(unit)
        unit = get_unit()
    print('propped_unit:', propped_unit)

def resol_conflict():
    conflict = get_conflict()
    print('conflict:', conflict)
    if conflict != None:
        return learning_procedure(conflict)
    return None

def choose_atom():
    print('A in choose:', A)
    for clause in F:
        for lit in clause:
            if A[abs(lit)] == -1:
                return abs(lit)

def backtrack(p):
    i = len(assignments) - 1
    while i >= 0:
        x = assignments.pop()
        A[abs(x)] = -1
        if abs(x) == p:
            break

def dpll():
    print('F:', F)
    print('A:', A)
    unit_prop()

    if all_sat():
        print('sat:', A[1:])
        exit()
    
    learned = resol_conflict()
    if learned != None and len(learned) == 0:
        print('unsat')
        exit()
    elif not learned:
        p = choose_atom()
        print(f'assigning {p} to be true')
        A[p] = 1
        assignments.append(p)
        dpll()

        backtrack(p)
        print(f'assigning {p} to be false')
        A[p] = 0
        dpll()

dpll()

# TODO: deal with empty clause