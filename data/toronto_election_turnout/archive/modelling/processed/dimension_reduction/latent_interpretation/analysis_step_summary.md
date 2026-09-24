# Latent Interpretation Step Summary

1. Located existing outputs: found prior summaries, loadings, VIP tables, interaction screens, and PCA/sparse PLS comparison artifacts under `data/toronto_election_turnout/modelling/processed/dimension_reduction`.
2. Created structure: wrote this analysis to `data/toronto_election_turnout/modelling/processed/dimension_reduction/latent_interpretation` and the script to `analysis/toronto_election_turnout/modelling/dimension_reduction/latent_interpretation`.
3. Selected representatives: interaction-augmented PLS has the highest CV R2 (0.566); theory-cleaned PLS is the main interpretation model because it is nearly as predictive and clearer; sparse PLS and supervised PCA are robustness/reference checks.
4. Interpreted latent compositions: Component 1 of cleaned PLS is the main turnout-resource/newcomer-fragmentation axis; Components 2-5 capture age/stability, urban form, service need, and secondary housing/service bundles.
5. Checked reference categories: high/low CT reference scores were generated from existing loadings and standardized existing predictors, not from newly trained models.
6. Compared model families: the same broad variables recur across PLS, sparse PLS, and PCA: visible minority share, bachelor-or-higher education, mayoral competitiveness, household size, non-citizenship, recent immigration, age, low income, and selected service-contact measures.
7. Interpreted interactions: the strongest interaction evidence concerns household/class variables with service-contact measures, especially low-income share times 311 requests per 1,000 residents.
8. Drafted main report: see `latent_variable_interpretation_report.md`.
9. Drafted benchmark comparison report: see `latent_model_comparison_report.md`.
