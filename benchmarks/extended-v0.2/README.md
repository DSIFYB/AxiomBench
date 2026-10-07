# Extended v0.2

900 original public synthetic tasks: 300 General, 300 Math, 150 C++ generation and 150 C++ repair. 75 underlying families, 90 family/mode groups, 10 variants each. Quick selects variant 1 of each group (90 items); Full selects all 900.

The compressed UTF-8 JSONL is read transparently by AxiomBench. `manifest.json` records exact bytes, counts and checksums. Source generator: `tools/build_extended.py`; trusted references: `references/`.

Reference test cases: 3900; the same cases are used for the paired repair tasks, giving 7800 cases across 300 C++ tasks. All 150 references passed and all 150 authored buggy variants were caught in local verification. All 300 mathematical answers were independently checked with a separate standard-library verifier. Human review, model calibration, expert general-knowledge coverage and hidden evaluation remain future work.

Difficulty tags are provisional. Variants are statistically dependent. No official third-party tasks or model scores are included. Public development scores cannot establish contamination-free intelligence, and the quick profile is for a broad smoke run rather than a precise ranking.
