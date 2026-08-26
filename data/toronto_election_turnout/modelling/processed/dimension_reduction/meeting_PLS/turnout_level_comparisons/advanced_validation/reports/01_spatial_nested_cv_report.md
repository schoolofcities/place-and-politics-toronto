# Step 1 Report: Spatially Blocked Nested Cross-Validation

## What has been done

The 585 CTs were joined to the project modelling geometry and divided into five deterministic compact geographic blocks. Each outer fold held out one complete block. Four inner geographic folds selected PLS component count, supervised-PCA screening/components, or elastic-net penalties using training geography only. Scaling and screening were refit inside the folds.

Block sizes were 77, 133, 94, 167, 114 CTs.

## Results

| Outcome | Method | Spatial CV R2 | RMSE | MAE | Residual neighbour correlation |
| --- | --- | --- | --- | --- | --- |
| Mean turnout | pls | 0.480 | 0.063 | 0.047 | 0.481 |
| Mean turnout | supervised_pca | 0.438 | 0.065 | 0.047 | 0.427 |
| Mean turnout | elastic_net | 0.442 | 0.065 | 0.049 | 0.511 |
| Municipal turnout | pls | 0.533 | 0.071 | 0.052 | 0.485 |
| Municipal turnout | supervised_pca | 0.584 | 0.067 | 0.050 | 0.499 |
| Municipal turnout | elastic_net | 0.486 | 0.074 | 0.055 | 0.559 |
| Provincial turnout | pls | 0.332 | 0.075 | 0.056 | 0.320 |
| Provincial turnout | supervised_pca | 0.301 | 0.077 | 0.058 | 0.326 |
| Provincial turnout | elastic_net | 0.303 | 0.077 | 0.058 | 0.351 |
| Federal turnout | pls | 0.263 | 0.085 | 0.065 | 0.363 |
| Federal turnout | supervised_pca | 0.219 | 0.088 | 0.068 | 0.448 |
| Federal turnout | elastic_net | 0.257 | 0.086 | 0.066 | 0.422 |

## Interpretation and analysis

These scores estimate transfer to an unseen part of Toronto, a harder task than predicting randomly withheld nearby CTs. Compared with the earlier shuffled PLS CV, R2 changed as follows: Mean turnout 0.534 to 0.480, Municipal turnout 0.629 to 0.533, Provincial turnout 0.371 to 0.332, Federal turnout 0.317 to 0.263. The decline is real but moderate, so spatial resemblance explains part—not all—of the earlier performance. Municipal turnout remains the most predictable and federal turnout the least predictable.

PLS had the strongest spatial R2 for every outcome (Federal turnout: pls, Mean turnout: pls, Municipal turnout: supervised_pca, Provincial turnout: pls). The residual-neighbour correlations remain between `0.320` and `0.559`, showing that omitted spatial structure still clusters geographically. The 14 variables do not exhaust Toronto's spatial organization.

## Further analysis

The selected setting for every outer block is stored separately. Large setting changes across blocks indicate tuning instability. Residual maps should be inspected before treating any citywide model as geographically generalizable.

## Conclusion

Spatial nested validation directly addresses geographic leakage and tuning optimism. It does not remove spatial structure or establish causality; it reveals how much of the apparent predictive signal survives when entire areas are unseen.
