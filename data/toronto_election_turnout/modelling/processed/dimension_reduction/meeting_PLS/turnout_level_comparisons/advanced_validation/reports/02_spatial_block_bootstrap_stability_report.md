# Step 2 Report: Spatial-Block Bootstrap Stability

## What has been done

The five geographic blocks were resampled with replacement 500 times. For each outcome, the meeting-variable PLS was refit using its selected compact component count. Component signs were aligned to the full-data solution before summarizing loadings. The outputs report median loadings, 95% spatial-bootstrap intervals, sign stability, and VIP intervals.

## Key results

| Outcome | Primary-component variable | Full loading | Lower 95% | Upper 95% | Sign stability |
| --- | --- | --- | --- | --- | --- |
| federal | average household size | -0.483 | -0.559 | -0.233 | 0.994 |
| federal | bachelor or higher education share | 0.440 | 0.257 | 0.507 | 0.998 |
| federal | visible minority share | -0.387 | -0.510 | -0.138 | 0.994 |
| federal | immigrant share | -0.383 | -0.497 | -0.020 | 0.978 |
| federal | same address five year share | -0.326 | -0.423 | -0.083 | 0.992 |
| mean | visible minority share | -0.516 | -0.543 | -0.351 | 1.000 |
| mean | immigrant share | -0.503 | -0.542 | -0.176 | 0.996 |
| mean | bachelor or higher education share | 0.438 | 0.226 | 0.472 | 1.000 |
| mean | average household size | -0.360 | -0.519 | 0.032 | 0.960 |
| mean | citizen adult share | 0.313 | 0.065 | 0.452 | 0.992 |
| municipal | visible minority share | -0.515 | -0.551 | -0.388 | 1.000 |
| municipal | immigrant share | -0.495 | -0.516 | -0.318 | 1.000 |
| municipal | citizen adult share | 0.415 | 0.338 | 0.451 | 1.000 |
| municipal | bachelor or higher education share | 0.353 | 0.121 | 0.461 | 1.000 |
| municipal | low income share | -0.328 | -0.410 | -0.181 | 1.000 |
| provincial | visible minority share | -0.492 | -0.539 | -0.193 | 0.996 |
| provincial | immigrant share | -0.484 | -0.554 | -0.041 | 0.984 |
| provincial | bachelor or higher education share | 0.437 | 0.240 | 0.472 | 1.000 |
| provincial | average household size | -0.409 | -0.577 | -0.028 | 0.984 |
| provincial | citizen adult share | 0.259 | -0.104 | 0.415 | 0.926 |

Across all variables and retained components, the share with at least 90% sign stability was federal: 71%, mean: 25%, municipal: 60%, provincial: 55%.

## Interpretation and analysis

A high sign-stability value means a variable remains on the same side of a component when entire Toronto regions are emphasized or omitted by resampling. The strongest primary anchors are highly stable: visible-minority and immigrant shares remain on the lower-turnout side, while bachelor-level education remains on the higher-turnout side across the outcome models. Municipal citizenship and low-income loadings are also especially stable; federal household size and residential stability are stable anchors of its more housing-oriented construction.

Narrow intervals indicate magnitude stability. Some smaller primary loadings and many later-component loadings cross zero, explaining why the overall 90%-stable share is lower for mean and provincial models. Those terms should not anchor the narrative even if their full-data loading appears non-zero.

## Further analysis

The primary component deserves the most narrative weight because later deflated components are usually less stable and have weaker direct outcome relationships. VIP stability should support variable ranking, while loading stability should support component naming; neither is a causal effect.

## Conclusion

The bootstrap distinguishes a reproducible citywide latent story from component details that depend on particular geographic blocks. Final prose should emphasize variables with stable direction and avoid over-interpreting unstable secondary loadings.
