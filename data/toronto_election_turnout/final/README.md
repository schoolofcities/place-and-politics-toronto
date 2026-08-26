# Final Toronto Census-Tract Turnout Data Release

This is the project’s analysis-ready release layer. Start here instead of
tracing the interpolation, variable-engineering, and model-development folders.
The release covers 585 analytical 2021 Toronto Census Tracts (CTs).

## Release Conventions

- `ct_id` is the canonical text join key for CT-wide tables.
- CSV files are the authoritative analytical tables.
- GeoJSON files repeat the corresponding table columns with EPSG:4326 geometry
  for immediate mapping.
- XLSX files are formatted convenience copies for direct review.
- CT election results are spatially allocated estimates, not official CT-level
  election returns.
- Results describe ecological associations and predictions, not individual or
  causal effects.

## Choose a Folder

| Folder | What it contains | Use it when |
| --- | --- | --- |
| `geography/` | Canonical CT identifiers, basic population context, and boundaries | You need a join base or map geometry |
| `observed/` | Cleaned Blocks 1–5 variables, CT election estimates, and candidate results | You need source-derived or engineered variables without model outputs |
| `modelled/` | PLS latent scores, fitted values, CV predictions, and residuals | You need CT-level outputs from the retained models |
| `meeting_pls/` | A compact 585-row handoff combining the 14 meeting variables, four outcomes, and meeting-PLS results | You want the simplest table for the meeting analysis |
| `model_definitions/` | Model summaries, predictor membership, component loadings, coefficients, VIP, and component labels | You need to interpret or reproduce the PLS models |
| `robustness_checks/` | Persisted supervised-PCA and Elastic Net spatial-CV results and definitions | You want method-dependence and geographic-generalization checks |
| `metadata/` | Dataset catalog, variable dictionary, QA results, and file manifests | You need exact definitions, lineage, or integrity checks |

Each subfolder has its own README with file grains, keys, column families,
interpretation notes, and join guidance. The top-level README intentionally
does not repeat those local data dictionaries.

## Recommended Starting Points

| Need | Start with |
| --- | --- |
| Map any CT dataset | `geography/toronto_ct_2021_geography.geojson` |
| Analyze all cleaned Blocks 1–5 variables | `observed/toronto_ct_2021_observed_variables.csv` |
| Analyze full election estimates | `observed/toronto_ct_election_results.csv` |
| Analyze candidates within CTs | `observed/toronto_ct_candidate_results.csv` |
| Use all retained PLS scores | `modelled/toronto_ct_latent_scores.csv` |
| Compare PLS predictions and residuals | `modelled/toronto_ct_turnout_model_results.csv` |
| Work directly on the meeting analysis | `meeting_pls/toronto_ct_meeting_pls.csv` |
| Map robustness residuals | `robustness_checks/toronto_ct_meeting_robustness_spatial_cv.geojson` |
| Look up one variable | `metadata/variable_dictionary.csv` |

## Joining and Mapping

CT-wide tables have one row per `ct_id` and can be joined one-to-one. The
candidate table is intentionally long and joins many-to-one to CT geography.
Keep identifiers as text. For nonspatial analysis, use CSV; for mapping, use an
existing GeoJSON or join the CSV to the canonical geography on `ct_id`.

## Outcome and Model Naming

- `participation_citizen_18plus` uses the estimated Canadian-citizen population
  aged 18+ as denominator.
- `turnout_electors` uses registered electors as denominator. Do not treat the
  two rates as interchangeable.
- Model columns identify the model, outcome, and quantity. Suffixes such as
  `_score`, `_percentile`, `_fitted_participation`, `_cv_prediction`, and
  `_residual` retain distinct meanings documented in the local READMEs.
- Component signs are orientation conventions. Interpret documented high and
  low loading sides rather than treating a positive score as inherently good.

## Rebuild and Refresh

From `analysis/toronto_election_turnout/`:

```bash
npm run build:final
```

To refresh only the robustness package from persisted model artifacts, without
fitting or predicting any model:

```bash
npm run build:final:collect-robustness
```

The release process does not alter raw or intermediate source data. File-level
sources and checksums are recorded under `metadata/`.
