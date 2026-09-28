// Data (clusters_summary.json, clusters_metadata.json, ct_clusters.geojson, ct_values.json)
// is all static, produced by analysis/clustering_neighbourhoods/process_ct_to_cluster.ipynb —
// so, like the site's other stories, this page can be fully prerendered.
export const prerender = true;

// while this page is behind <PasswordGate />, don't render its content into the
// HTML source — remove this line when the page goes public
export const ssr = false;
