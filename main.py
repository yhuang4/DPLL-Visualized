while True:
    sat_input = input().split()
    if len(sat_input) == 4 and sat_input[0] == 'p' and sat_input[1] == 'cnf':
        try:
            nbvar, nbclauses = int(sat_input[2]), int(sat_input[3])
            break
        except:
            pass
    print('Fomat error. Format: p cnf [nbvar] [nbclauses]')

for i in range(nbclauses):
    