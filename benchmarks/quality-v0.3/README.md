# Quality v0.3

1100 original public synthetic development tasks: General 350, Math 350, C++ generation 150, C++ repair 250. Repair includes 150 semantic and 100 syntax/compilation tasks. Quick selects one variant from each of 110 family/mode groups. There are 95 underlying families, not 1100 independently authored questions.

The ten previously constant-answer General families now contain varying premises or conclusions; boolean families are balanced 5/5. Five new reasoning and five new mathematics families require combined constraints, conditional probability, optimization and multistep processing.

All fifteen C++ algorithm families now include large or maximum-size stress cases. Runtime CPU budget is 1 second per case; Docker startup is excluded from this CPU budget. Host verification checks trusted references and rejects authored faulty and selected inefficient algorithms. These checks are not a formal complexity proof. Difficulty remains provisional.

Syntax repair requires full corrected C++20 source, successful compilation and correct output on all cases; merely deleting the problematic line is insufficient. No model answers are used to design these tasks. The suite remains public dev: do not train on it and claim a held-out score. Old v0.1 and v0.2 datasets remain frozen. v0.3 scores must be reported separately.
