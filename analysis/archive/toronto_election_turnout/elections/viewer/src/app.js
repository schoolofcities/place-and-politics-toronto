const datasets = {
  municipal: {
    label: "Municipal 2023 Mayor",
    url: "/data/toronto_election_turnout/elections/processed/municipal_2023_mayor/turnout/toronto_municipal_2023_mayor_turnout_subdivisions.geojson",
    districtUrl: "/data/toronto_election_turnout/elections/processed/municipal_2023_mayor/turnout/toronto_municipal_2023_mayor_turnout_subdivisions_districts.json",
    districtLabel: "Ward"
  },
  provincial: {
    label: "Provincial 2025",
    url: "/data/toronto_election_turnout/elections/processed/provincial_2025/turnout/toronto_provincial_2025_turnout_poll_divisions.geojson",
    districtUrl: "/data/toronto_election_turnout/elections/processed/provincial_2025/turnout/toronto_provincial_2025_turnout_poll_divisions_districts.json",
    districtLabel: "Riding"
  },
  federal: {
    label: "Federal 2025",
    url: "/data/toronto_election_turnout/elections/processed/federal_2025/turnout/toronto_federal_2025_turnout_poll_divisions.geojson",
    districtUrl: "/data/toronto_election_turnout/elections/processed/federal_2025/turnout/toronto_federal_2025_turnout_poll_divisions_districts.json",
    districtLabel: "Riding"
  }
};

const datasetNotes = {
  municipal: [
    "Found official-source mismatch: Toronto's final voter-statistics workbook reports 724,638 voters and 1,947,242 eligible electors, producing 37.2% turnout. Toronto's December 2023 report describes final turnout as 37%.",
    "The often-cited 38.5% turnout used an earlier, smaller elector denominator. It is not substituted into subdivision rows.",
    "Toronto's report states 725,333 ballots cast, but its method totals and released row-level workbooks total 724,638. The unexplained 695-ballot difference is not assigned to subdivisions."
  ],
  provincial: [
    "Advance-vote reporting buckets are included in totals but usually have no separate elector denominator or ordinary polling-division polygon.",
    "Combined polls remain visible as no-data areas when their results are officially reported with another division."
  ],
  federal: [
    "Federal ordinary polling-division names are usually reported as Toronto in Elections Canada Format 2; mobile and special-group labels are preserved where available.",
    "Advance and some special-voting buckets are included in vote totals but have no supported turnout denominator or ordinary polling-division polygon.",
    "Combined-source rows remain visible and point to the division where their official results are reported."
  ]
};

const state = {
  key: "municipal",
  data: {},
  districts: {},
  layer: null,
  dotLayer: null,
  district: "all",
  voteType: "all",
  minTurnout: 0,
  showDots: false
};

const map = L.map("map", {
  preferCanvas: true,
  zoomControl: true
}).setView([43.71, -79.38], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const els = {
  dataset: document.getElementById("datasetSelect"),
  district: document.getElementById("districtSelect"),
  voteType: document.getElementById("voteTypeSelect"),
  min: document.getElementById("minTurnout"),
  dots: document.getElementById("dotToggle"),
  minLabel: document.getElementById("minTurnoutLabel"),
  count: document.getElementById("statCount"),
  noData: document.getElementById("statNoData"),
  average: document.getElementById("statAverage"),
  votes: document.getElementById("statVotes"),
  electors: document.getElementById("statElectors"),
  status: document.getElementById("status"),
  notes: document.getElementById("datasetNotes")
};

function fmtNumber(value) {
  if (value === null || value === undefined || value === "") return "No data";
  return Number(value || 0).toLocaleString("en-CA");
}

function fmtPct(value) {
  return value === null || value === undefined || Number.isNaN(value)
    ? "No data"
    : `${(Number(value) * 100).toFixed(1)}%`;
}

function turnoutValue(properties) {
  const raw = properties.proportion_of_turnout;
  if (raw === null || raw === undefined || raw === "") return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}

function countsInTotals(properties) {
  return !String(properties.vote_in_other_division || "").trim();
}

function turnoutColor(value) {
  if (value === null || value === undefined || Number.isNaN(value)) return "#f3efe5";
  if (value < 0.30) return "#d73027";
  if (value < 0.40) return "#fc8d59";
  if (value < 0.50) return "#fee08b";
  if (value < 0.60) return "#91cf60";
  return "#1a9850";
}

function styleFeature(feature) {
  const turnout = turnoutValue(feature.properties);
  return {
    color: "#47534b",
    weight: 0.55,
    opacity: 0.7,
    fillColor: turnoutColor(turnout),
    fillOpacity: 0.72
  };
}

function districtName(properties) {
  const id = properties.electoral_district_number || "";
  const name = state.districts[state.key]?.get(String(id)) || "Unknown";
  return `${id} - ${name}`;
}

function popupHtml(properties) {
  const division = properties.polling_division_number || "Unknown";
  const voteType = properties.vote_type
    ? `<tr><th>Voting method</th><td>${properties.vote_type.replaceAll("_", " ")}</td></tr>`
    : "";
  const pollingName = properties.polling_division_name
    ? `<tr><th>Polling place</th><td>${properties.polling_division_name}</td></tr>`
    : "";
  const note = properties.source_note
    ? `<tr><th>Note</th><td>${properties.source_note}</td></tr>`
    : "";
  return `
    <h3 class="popup-title">${districtName(properties)}</h3>
    <table class="popup-table">
      <tr><th>Polling division</th><td>${division}</td></tr>
      ${pollingName}
      ${voteType}
      <tr><th>Turnout</th><td>${fmtPct(turnoutValue(properties))}</td></tr>
      <tr><th>Votes</th><td>${fmtNumber(properties.number_of_votes)}</td></tr>
      <tr><th>Electors</th><td>${fmtNumber(properties.number_of_electors)}</td></tr>
      <tr><th>Combined with</th><td>${properties.vote_in_other_division || "None"}</td></tr>
      ${note}
    </table>
  `;
}

function featurePasses(feature) {
  const p = feature.properties;
  if (state.district !== "all" && String(p.electoral_district_number) !== state.district) {
    return false;
  }
  if (state.voteType !== "all" && String(p.vote_type || "") !== state.voteType) {
    return false;
  }
  const turnout = turnoutValue(p);
  if (turnout === null) {
    return state.minTurnout === 0;
  }
  if (turnout * 100 < state.minTurnout) {
    return false;
  }
  return true;
}

function selectedRows() {
  const data = state.data[state.key];
  return data.features.filter(featurePasses);
}

function selectedMappedFeatures(rows) {
  return rows.filter((feature) => feature.geometry);
}

function updateStats(rows, mappedCount) {
  const totals = rows.reduce((acc, feature) => {
    const p = feature.properties;
    const turnout = turnoutValue(p);
    if (turnout === null) {
      acc.noData += 1;
    }
    if (countsInTotals(p)) {
      acc.votes += Number(p.number_of_votes || 0);
      acc.electors += Number(p.number_of_electors || 0);
    }
    return acc;
  }, { votes: 0, electors: 0, noData: 0 });

  els.count.textContent = fmtNumber(mappedCount);
  els.noData.textContent = fmtNumber(totals.noData);
  els.votes.textContent = fmtNumber(totals.votes);
  els.electors.textContent = fmtNumber(totals.electors);
  els.average.textContent = totals.electors && totals.votes <= totals.electors
    ? fmtPct(totals.votes / totals.electors)
    : "--";
}

function dotRadius(votes) {
  const value = Number(votes || 0);
  if (!Number.isFinite(value) || value <= 0) return 0;
  return Math.max(3, Math.min(18, Math.sqrt(value) / 3.8));
}

function drawDots() {
  if (state.dotLayer) {
    state.dotLayer.remove();
    state.dotLayer = null;
  }
  if (!state.showDots || !state.layer) return;

  const markers = [];
  state.layer.eachLayer((divisionLayer) => {
    if (!divisionLayer.getBounds) return;
    const props = divisionLayer.feature.properties;
    const radius = dotRadius(props.number_of_votes);
    if (!radius) return;
    markers.push(
      L.circleMarker(divisionLayer.getBounds().getCenter(), {
        radius,
        color: "#234a8f",
        weight: 1.6,
        fillColor: "#234a8f",
        fillOpacity: 0.24,
        opacity: 0.72
      }).bindPopup(popupHtml(props))
    );
  });

  state.dotLayer = L.layerGroup(markers).addTo(map);
}

function renderDistrictOptions() {
  const rows = Array.from(state.districts[state.key].entries())
    .map(([id, name]) => [id, `${id} - ${name}`])
    .sort((a, b) => a[1].localeCompare(b[1]));

  els.district.innerHTML = `<option value="all">All Toronto divisions</option>` +
    rows.map(([id, label]) => `<option value="${id}">${label}</option>`).join("");
  els.district.value = "all";
  state.district = "all";
}

function renderDatasetNotes() {
  els.notes.innerHTML = `<ul>${datasetNotes[state.key]
    .map((note) => `<li>${note}</li>`)
    .join("")}</ul>`;
}

function draw() {
  const rows = selectedRows();
  const features = selectedMappedFeatures(rows);
  if (state.layer) {
    state.layer.remove();
  }
  if (state.dotLayer) {
    state.dotLayer.remove();
    state.dotLayer = null;
  }

  state.layer = L.geoJSON({ type: "FeatureCollection", features }, {
    style: styleFeature,
    onEachFeature(feature, layer) {
      layer.bindPopup(popupHtml(feature.properties));
      layer.on({
        mouseover(event) {
          event.target.setStyle({ weight: 2, color: "#13251f", fillOpacity: 0.9 });
          event.target.bringToFront();
        },
        mouseout(event) {
          state.layer.resetStyle(event.target);
        }
      });
    }
  }).addTo(map);

  updateStats(rows, features.length);
  els.status.textContent = `${datasets[state.key].label}: ${fmtNumber(features.length)} mapped divisions shown`;
  drawDots();

  if (features.length) {
    map.fitBounds(state.layer.getBounds(), { padding: [18, 18] });
  }
}

async function loadDataset(key) {
  if (state.data[key]) return;
  els.status.textContent = `Loading ${datasets[key].label}...`;
  const [dataResponse, districtResponse] = await Promise.all([
    fetch(datasets[key].url),
    fetch(datasets[key].districtUrl)
  ]);
  if (!dataResponse.ok) throw new Error(`Could not load ${datasets[key].url}`);
  if (!districtResponse.ok) throw new Error(`Could not load ${datasets[key].districtUrl}`);
  state.data[key] = await dataResponse.json();
  const districts = await districtResponse.json();
  state.districts[key] = new Map(districts.map((row) => [
    String(row.electoral_district_number),
    row.electoral_district_name
  ]));
}

async function changeDataset(key) {
  state.key = key;
  await loadDataset(key);
  renderDistrictOptions();
  renderDatasetNotes();
  draw();
}

els.dataset.addEventListener("change", (event) => {
  changeDataset(event.target.value).catch((error) => {
    els.status.textContent = error.message;
    console.error(error);
  });
});

els.district.addEventListener("change", (event) => {
  state.district = event.target.value;
  draw();
});

els.voteType.addEventListener("change", (event) => {
  state.voteType = event.target.value;
  draw();
});

els.min.addEventListener("input", (event) => {
  state.minTurnout = Number(event.target.value);
  els.minLabel.textContent = `${state.minTurnout}%`;
  draw();
});

els.dots.addEventListener("change", (event) => {
  state.showDots = event.target.checked;
  drawDots();
});

changeDataset(state.key).catch((error) => {
  els.status.textContent = error.message;
  console.error(error);
});
