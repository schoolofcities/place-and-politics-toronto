# Supervised Dimension Reduction

This folder contains the CT-level supervised dimension-reduction workflow for mean turnout.

Run from the repository root:

```bash
/Users/kevinyang/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 analysis/toronto_election_turnout/modelling/dimension_reduction/scripts/run_dimension_reduction_workflow.py
```

The script writes outputs to:

```text
data/toronto_election_turnout/modelling/processed/dimension_reduction/
```

Main reports:

- `reports/task1_full_pls_summary.md`
- `reports/task2_multicollinearity_diagnostics.md`
- `reports/task3_theory_cleaned_pls_report.md`

