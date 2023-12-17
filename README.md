# DPLL-Visualized

A DPLL SAT Solver with clause learning and decision visualization. 

Implemented the algorithm described in https://www.cs.ox.ac.uk/people/james.worrell/lec7-2015.pdf.

Referenced https://www.cs.cmu.edu/~15414/f17/lectures/10-dpll.pdf.

Read https://github.com/sukrutrao/SAT-Solver-DPLL?tab=readme-ov-file for implmentation inspiration.

## Run the solver

Including `-p` visualizes the decision process.

```
$ python3 main.py [path_to_cnf] [-p]
```

### Input format

The input is in cnf format. Refer to http://www.satcompetition.org/2009/format-benchmarks2009.html for detailed description.

### Sample files

Sample cnf files can be found in `examples`. For more test cases, visit https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html. 

## Implementation

There are a lot of variations of DPLL. As mentioned earlier, the main strategy to cut down the search space besides unit propogation is clause learning. 

The main idea behind clause learning is to avoid identical decision errors by analyzing a conflict clause. Oftentimes simply backtracking to the previous level doesn't solve the root cause of the conflict, so we will encouter the same conflict in the future even though the assignments are different. Hence we analyze the conflict clause and add the learned clause to the formula as a restriction to avoid making the same error.

## Decision visualization

Including `-p` when running the file will give you a visualization of the decision process. You will be able to see what variables are being unit-propogated in what order, and what clause is learned from what conflict.

Additionally, it will print out a decision tree that includes all the decision variables.

## Future work

Much of the effort went into ensuring the correctness of clause learning, and therefore other common heuristics haven't been implmented. For example, a common strategy of choosing the next unassigned varialbe is basing off its frequency in the formula. That will play nicely with the visulaiztion. 
