def read_cnf_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extracting information from the header
    num_vars, num_clauses = 0, 0
    for line in lines:
        if line.startswith('p cnf'):
            _, num_vars, num_clauses = line.split()[1:]
            break

    # Parsing clauses
    clauses = []
    for line in lines:
        if not line.startswith(('c', 'p')):
            clause = list(map(int, line.split()[:-1]))
            clauses.append(clause)

    return int(num_vars), int(num_clauses), clauses

# Example usage
# file_path = 'cnfs/uf20-01.cnf'
# num_vars, num_clauses, clauses = read_cnf_file(file_path)

# print(f'Number of variables: {num_vars}')
# print(f'Number of clauses: {num_clauses}')
# print('Clauses:')
# for clause in clauses:
#     print(clause)