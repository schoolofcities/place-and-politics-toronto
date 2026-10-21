# The Five Torontos (Part 7)

Front end for [The Five Torontos](https://schoolofcities.github.io/place-and-politics-toronto/five-torontos): Toronto's 585 census tracts clustered into five political geographies from their voting and turnout in the 2023 mayoral by-election and the 2025 provincial and federal elections. The full methods are in [`analysis/clustering_neighbourhoods/DATA_AND_METHODS.md`](../../../analysis/clustering_neighbourhoods/DATA_AND_METHODS.md); this page links to them from its own "Data and methods" note.

SvelteKit ignores this file (it has no `+` prefix), so it is safe to keep here.

## Layout

```
five-torontos/
├── +page.svelte        the page: copy, metadata, and the order of sections
├── +page.js            prerender = true (the page is rendered to static HTML at build time)
├── sections.js         per-cluster config: which voting rows and which strip plot each section shows
├── data/               static data, written by analysis/clustering_neighbourhoods/04_process_ct_to_cluster.ipynb
└── components/
    ├── ClusterMap.svelte             map of the clusters (rotating intro map, single-cluster section maps)
    ├── VotingDumbbell.svelte         cluster vs. Toronto dumbbell chart of a section's voting rows
    ├── StripPlot.svelte              one dot per tract on 2–3 census variables, cluster highlighted
    ├── ClusterSummaryTable.svelte    a section's full election tables / census table, behind toggles
    ├── ClusterComparisonTables.svelte  all five clusters side by side
    ├── SectionNav.svelte             "On this page" menu (scrollspy)
    ├── clusterColors.js              the page's cluster palette (overrides colours in the data files)
    └── clusterVariables.js           which election rows and census rows the tables show, and their formatting
```

## Data

Everything in `data/` is produced by notebook `04_process_ct_to_cluster.ipynb` (inputs are in the git-ignored `data/clustering_neighbourhoods/`). Nothing is fetched at runtime.

| File | What it is | Used by |
| --- | --- | --- |
| `clusters_summary.json` | one record per cluster: size, population, vote shares and turnout, census values, deviations from Toronto | page, tables, dumbbell |
| `clusters_metadata.json` | Toronto-wide benchmark, `variable_labels`, methods summary, notes | page, tables, dumbbell |
| `ct_values.json` | one record per tract with the census and election values the strip plots use | strip plots |
| `ct_clusters.geo.json` | tract outlines with their cluster | map |
| `clusters_dissolved.geo.json` | tracts dissolved into one shape per cluster | map |
| `wards.geo.json`, `fed_2025.geo.json`, `former_municipalities.geo.json` | the map's "Reference layers" | map |

How the numbers are defined:

- **Vote shares** are weighted by valid votes cast in each tract.
- **Turnout** is total votes cast divided by Canadian citizens aged 18+ (not registered electors), at tract, cluster and Toronto level. Anywhere turnout is labelled on the page it says "citizens 18+".
- **Mayoral candidates** are Chow, Bailão, Saunders, Furey, Matlow and "Other candidates". The tables list all of them, so each election's rows add up to about 100%.
- **Income** (`income_median_approx`, shown as "Median pre-tax individual income") is the 2021 Census median total income in 2020 among recipients aged 15+. A cluster's figure is the population-weighted average of its tracts' medians, not a recomputed median.
- Cluster membership comes from the saved Model 8F, not from the page. Census values only describe the clusters.

## Editing

| To change… | Edit |
| --- | --- |
| Body copy, headings, the methods note | `+page.svelte` (the text for each cluster is in the `{#if cluster.slug === …}` chain) |
| Which voting rows a section's dumbbell shows, or its strip-plot variables | `sections.js` |
| Row labels in the election tables, or which candidates/parties appear | `ELECTIONS` in `components/clusterVariables.js` |
| Labels like "2023 mayoral turnout (citizens 18+)" or the income label | `variable_labels` in `data/clusters_metadata.json` (and the same dictionary in notebook 04, so a re-run doesn't undo it) |
| Census rows in the tables, or how a value is formatted | `SOCIOECONOMIC_KEYS` and the formatters in `components/clusterVariables.js` |
| Cluster colours | `components/clusterColors.js` |
| The intro map's rotation speed | `setInterval` in `+page.svelte` |

If the data changes, re-run notebook 04 rather than editing the JSON by hand, then rebuild.

## Metadata and the series

- Title, description, Open Graph and Twitter tags are set in `<svelte:head>` in `+page.svelte`; the canonical link and JSON-LD come from `<StructuredData slug="five-torontos" />`.
- The post's title, date, thumbnail and byline are in `src/lib/posts.js`, which drives the home page list, the footer on every page and the JSON-LD.
- The social card is `src/assets/web-card-7.png` (1200×628); the home-page thumbnail is `src/assets/p7.png`. Link previews use the `raw.githubusercontent.com/.../main/` URL, so both must be pushed to `main`.
- The home page entry for Part 7 is in `src/routes/+page.svelte`.

## Behaviour worth knowing

- The page is prerendered, so anything that needs the browser (the map shapes, strip plots) is drawn only after mount. Don't use `Math.random()` for element ids: they would differ between the server HTML and the browser (the table toggles use `part` + the cluster slug).
- The map, tables and strip plots all read the same cluster records, so a change in `data/` shows up everywhere at once.
- The "Reference layers" buttons only affect the map they sit under. Boundary names appear only when the map is wide enough for them not to overlap (`labelMinWidth` in `ClusterMap.svelte`).

## Building

The production build writes to `docs/` (GitHub Pages) and needs a current Node (the site uses Vite 6, which fails on Node 17; it was last built here with Node 22). `npm run build`, then commit `docs/` with the source change.
