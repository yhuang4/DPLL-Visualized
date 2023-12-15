def read_cnf_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extracting information from the header
    for i, line in enumerate(lines):
        if line.startswith('p cnf'):
            nbvar, nbclauses = map(int, line.split()[2:])
            start = i
            break

    clauses = []
    for i in range(start + 1, start + nbclauses + 1):
        line = lines[i]
        clause = list(map(int, line.split()[:-1]))
        clauses.append(clause)
        
    return nbvar, nbclauses, clauses

# Example usage
# file_path = 'cnfs/uf20-01.cnf'
# num_vars, num_clauses, clauses = read_cnf_file(file_path)

# print(f'Number of variables: {num_vars}')
# print(f'Number of clauses: {num_clauses}')
# print('Clauses:')
# for clause in clauses:
#     print(clause)