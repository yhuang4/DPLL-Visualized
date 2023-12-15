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
import os
import sys
sys.setrecursionlimit(10000)
# nbvar, nbclauses = map(int, input().split())

# F = []
# A = [-1] * (nbvar + 1)
# for i in range(nbclauses):
#     clause = list(map(int, input().split()))[:-1]  # Terminated by a 0
#     F.append(clause)

nbvar, nbclauses, F = read_cnf_file('UUF50.218.1000/uuf50-01.cnf')
# nbvar, nbclauses, F = read_cnf_file('cnfs/uf20-0744.cnf')

assignments = []
implied = []
A = [-1] * (nbvar + 1)
F_test = copy.deepcopy(F)

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
            # implied[abs(unassigned)] = i
            implied.append((abs(unassigned), i))
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
    # print('A:', A)
    count = 0
    for clause in F:
        # print('clause:', clause)
        count += 1
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
    # print(count)
    return None

def learning_procedure(C):
    C = copy.deepcopy(C)
    # C.sort(key=lambda x: abs(x), reverse=True)
    def get_implied():
        for (x, i) in reversed(implied):
            if x in C:
                return (x, i)
            if -x in C:
                return (-x, i)
        # for lit in C:
        #     if abs(lit) in implied:
        #         return lit
        return None
    
    def resolve(C_prime, l):
        C.remove(l)
        for lit in C_prime:
            if abs(lit) != abs(l):
                if -lit in C:
                    C.remove(-lit)
                elif lit in C:
                    C.remove(lit)
                if lit not in C:
                    C.append(lit)
    
    # print('C:', C)
    l = get_implied()
    # print('l:', l)
    while l != None:
        # C_prime = F[implied[abs(l)]]
        l, i = l
        C_prime = F[i]
        # print('C:', C)
        # print('C\':', C_prime)
        resolve(C_prime, l)
        l = get_implied()
        # print('l:', l)
    # print('learned', C)
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

def resol_conflict():
    conflict = get_conflict()
    # print('conflict:', conflict)
    if conflict != None:
        return learning_procedure(conflict)
    return None

def choose_atom():
    # print('A in choose:', A)
    for clause in F:
        for lit in clause:
            if A[abs(lit)] == -1:
                return abs(lit)

def backtrack(p):
    i = len(assignments) - 1
    while i >= 0:
        x = assignments.pop()
        j = len(implied) - 1
        while j >= 0:
            y, _ = implied[j]
            if abs(x) == abs(y):
                implied.pop(j)
            j -= 1
        A[abs(x)] = -1
        if abs(x) == p:
            break

def proofread():
    for clause in F_test:
        sat = False
        for lit in clause:
            if lit > 0 and A[lit] == 1:
                sat = True
                break
            elif lit < 0 and A[abs(lit)] == 0:
                sat = True
                break
        if not sat:
            return False
    return True

def dpll():
    # print('F:', F)
    unit_prop()

    if all_sat():
        print('sat:', A[1:])
        print('proofread:', proofread())
        exit()
    
    learned = resol_conflict()
    # print('learned:', learned)
    # if A[2] == 0: print('F:', F)
    if learned != None and len(learned) == 0:
        print('unsat')
        exit()
    elif not learned:
        p = choose_atom()
        # print(f'assigning {p} to be true')
        A[p] = 1
        assignments.append(p)
        dpll()
        backtrack(p)

        # print(f'assigning {p} to be false')
        A[p] = 0
        assignments.append(p)
        dpll()
        backtrack(p)

dpll()
print('unsat')

# TODO: deal with empty clause

