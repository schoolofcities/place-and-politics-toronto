# Meeting-Variable Turnout-Level Comparisons

This folder contains separately supervised meeting-variable models for mean,
municipal, provincial, and federal CT turnout. Each outcome has PLS,
correlation-screened supervised PCA, and elastic-net robustness artifacts.

The four interpretation reports are under `reports/`. The three level-specific
reports compare one election level with mean turnout; the consolidated report
is a short audience-facing synthesis rather than a stack of the detailed
reports. A separate methodology note specifies spatially blocked nested CV and
domain-importance next steps. No cross-level difference outcome is fitted.

Rebuild from the repository root with:

```bash
/opt/anaconda3/bin/python3 analysis/toronto_election_turnout/modelling/dimension_reduction/meeting_PLS/run_turnout_level_comparisons.py
```

PLS component selection searches one through five components using the
repository's fixed shuffled 10-fold CV convention. Component signs are aligned
before level-versus-mean loading comparisons. Supervised PCA and elastic net
are exploratory robustness checks; see the reports for validation caveats.
