const sources = {
  da: {
    label: "Dissemination Areas",
    url: "/data/toronto_election_turnout/census/processed/da/statcan_2021_toronto_da.geojson"
  },
  ct: {
    label: "Census Tracts",
    url: "/data/toronto_election_turnout/census/processed/ct/statcan_2021_toronto_ct.geojson"
  },
  ada: {
    label: "Aggregate Dissemination Areas",
    url: "/data/toronto_election_turnout/census/processed/ada/statcan_2021_toronto_ada.geojson"
  }
};

const state = { level: "da", metric: "citizens", data: {}, layer: null, overlay: null };
const metricMeta = {
  citizens: {
    label: "Canadian citizens aged 18+",
    shortLabel: "Citizens aged 18+",
    missingLabel: "Suppressed / unpublished",
    value(feature) {
      const p = feature.properties;
      return state.level === "ada"
        ? p.ada_profile_citizen_canadian_18over
        : p.citizen_canadian_18over;
    },
    status(feature) {
      return feature.properties.value_status;
    },
    note(feature) {
      return feature.properties.source_note;
    }
  },
  population18: {
    label: "All residents aged 18+",
    shortLabel: "Residents aged 18+",
    missingLabel: "Suppressed / incomplete",
    value(feature) {
      return feature.properties.population_18plus;
    },
    status(feature) {
      return feature.properties.population_18plus_value_status;
    },
    note(feature) {
      return feature.properties.population_18plus_source_note;
    }
  }
};
const colors = ["#edf5e9", "#b8dfc0", "#6fb9a5", "#32858a", "#294c73"];
const map = L.map("map", { preferCanvas: true }).setView([43.71, -79.38], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const els = {
  level: document.getElementById("levelSelect"),
  metric: document.getElementById("metricSelect"),
  overlay: document.getElementById("adaOverlay"),
  count: document.getElementById("statCount"),
  missing: document.getElementById("statMissing"),
  citizens: document.getElementById("statCitizens"),
  area: document.getElementById("statArea"),
  valueLabel: document.getElementById("statValueLabel"),
  legendTitle: document.getElementById("legendTitle"),
  legendRows: document.getElementById("legendRows"),
  status: document.getElementById("status")
};

function fmt(value, digits = 0) {
  if (value === null || value === undefined || value === "") return "No data";
  return Number(value).toLocaleString("en-CA", { maximumFractionDigits: digits });
}

function activeMetric() {
  return metricMeta[state.metric] || null;
}

function metricValue(feature) {
  if (state.metric === "none") return null;
  if (state.metric === "area") return Number(feature.properties.LANDAREA);
  const metric = activeMetric();
  const value = metric ? metric.value(feature) : null;
  return value === null || value === undefined ? null : Number(value);
}

function quantiles(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return [];
  return [0, 0.25, 0.5, 0.75, 1].map((q) => {
    const index = Math.min(sorted.length - 1, Math.floor(q * (sorted.length - 1)));
    return sorted[index];
  });
}

function colorFor(value, breaks) {
  if (!Number.isFinite(value) || !breaks.length) return "#f3efe5";
  for (let i = 1; i < breaks.length; i += 1) {
    if (value <= breaks[i]) return colors[i - 1];
  }
  return colors[colors.length - 1];
}

function popup(feature) {
  const p = feature.properties;
  const relationship = state.level === "da"
    ? `<tr><th>CT</th><td>${p.ct_id}</td></tr><tr><th>ADA</th><td>${p.ada_id}</td></tr>`
    : state.level === "ct"
      ? `<tr><th>ADA</th><td>${p.ada_id || "No link"}</td></tr>`
      : `<tr><th>Component CTs</th><td>${fmt(p.component_ct_count)}</td></tr>
         <tr><th>Component DAs</th><td>${fmt(p.component_da_count)}</td></tr>
         <tr><th>DA-summed citizens</th><td>${fmt(p.da_sum_citizen_canadian_18over)}</td></tr>`;
  const status = p.value_status && p.value_status !== "published"
    ? `<tr><th>Citizen value status</th><td>${p.value_status}</td></tr>`
    : "";
  const populationStatus = p.population_18plus_value_status && p.population_18plus_value_status !== "published"
    ? `<tr><th>Resident 18+ status</th><td>${p.population_18plus_value_status}</td></tr>`
    : "";
  const note = p.source_note
    ? `<tr><th>Source note</th><td>${p.source_note}</td></tr>`
    : "";
  const populationNote = p.population_18plus_source_note
    ? `<tr><th>Resident 18+ note</th><td>${p.population_18plus_source_note}</td></tr>`
    : "";
  return `
    <h3 class="popup-title">${p.geo_level} ${p.geo_id}</h3>
    <table class="popup-table">
      <tr><th>Citizens aged 18+</th><td>${fmt(metricMeta.citizens.value(feature))}</td></tr>
      <tr><th>Residents aged 18+</th><td>${fmt(metricMeta.population18.value(feature))}</td></tr>
      <tr><th>Land area (km²)</th><td>${fmt(p.LANDAREA, 3)}</td></tr>
      ${relationship}
      ${status}
      ${populationStatus}
      ${note}
      ${populationNote}
    </table>`;
}

function renderLegend(breaks) {
  const title = state.metric === "area"
    ? "Land area (km²)"
    : state.metric === "none" ? "Boundaries" : activeMetric().label;
  els.legendTitle.textContent = title;
  if (!breaks.length) {
    els.legendRows.innerHTML = `<div class="legend-row"><i style="background:#dce8e1"></i><span>Geography boundary</span></div>`;
    return;
  }
  els.legendRows.innerHTML = colors.slice(0, breaks.length - 1).map((color, i) =>
    `<div class="legend-row"><i style="background:${color}"></i><span>${fmt(breaks[i], 2)} – ${fmt(breaks[i + 1], 2)}</span></div>`
  ).join("") + `<div class="legend-row"><i style="background:#f3efe5"></i><span>Suppressed / not published</span></div>`;
}

function updateStats(features) {
  const metric = activeMetric();
  const analysisFeatures = state.level === "ct"
    ? features.filter((feature) => feature.properties.contains_toronto_da)
    : features;
  const values = metric ? analysisFeatures.map((f) => metric.value(f)) : [];
  const areas = analysisFeatures.map((f) => Number(f.properties.LANDAREA)).filter(Number.isFinite).sort((a, b) => a - b);
  const validValues = values.filter((v) => v !== null && v !== undefined).map(Number);
  els.count.textContent = fmt(analysisFeatures.length);
  els.missing.textContent = metric ? fmt(values.length - validValues.length) : "0";
  els.valueLabel.textContent = metric ? metric.shortLabel : "Mapped value";
  els.citizens.textContent = metric ? fmt(validValues.reduce((sum, value) => sum + value, 0)) : "No data";
  els.area.textContent = areas.length ? `${fmt(areas[Math.floor(areas.length / 2)], 3)} km²` : "No data";
}

async function load(level) {
  if (state.data[level]) return state.data[level];
  const response = await fetch(sources[level].url);
  if (!response.ok) throw new Error(`Could not load ${sources[level].label}`);
  state.data[level] = await response.json();
  return state.data[level];
}

async function drawOverlay() {
  if (state.overlay) {
    state.overlay.remove();
    state.overlay = null;
  }
  if (!els.overlay.checked || state.level === "ada") return;
  const data = await load("ada");
  state.overlay = L.geoJSON(data, {
    interactive: false,
    style: { color: "#151a18", weight: 2, opacity: 0.8, fillOpacity: 0 }
  }).addTo(map);
}

async function draw() {
  const data = await load(state.level);
  const features = data.features;
  const breaks = state.metric === "none" ? [] : quantiles(features.map(metricValue));
  if (state.layer) state.layer.remove();
  state.layer = L.geoJSON(data, {
    style(feature) {
      return {
        color: "#43544b",
        weight: state.level === "da" ? 0.45 : 0.8,
        opacity: 0.75,
        fillColor: state.metric === "none" ? "#dce8e1" : colorFor(metricValue(feature), breaks),
        fillOpacity: state.metric === "none" ? 0.35 : 0.72
      };
    },
    onEachFeature(feature, layer) {
      layer.bindPopup(popup(feature));
      layer.on({
        mouseover(event) { event.target.setStyle({ weight: 2, color: "#111815", fillOpacity: 0.9 }); },
        mouseout(event) { state.layer.resetStyle(event.target); }
      });
    }
  }).addTo(map);
  renderLegend(breaks);
  updateStats(features);
  els.status.textContent = `${sources[state.level].label}: ${fmt(features.length)} areas shown`;
  map.fitBounds(state.layer.getBounds(), { padding: [18, 18] });
  await drawOverlay();
}

els.level.addEventListener("change", (event) => {
  state.level = event.target.value;
  draw().catch((error) => { els.status.textContent = error.message; console.error(error); });
});
els.metric.addEventListener("change", (event) => {
  state.metric = event.target.value;
  draw().catch((error) => { els.status.textContent = error.message; console.error(error); });
});
els.overlay.addEventListener("change", () => {
  drawOverlay().catch((error) => { els.status.textContent = error.message; console.error(error); });
});

draw().catch((error) => {
  els.status.textContent = error.message;
  console.error(error);
});
