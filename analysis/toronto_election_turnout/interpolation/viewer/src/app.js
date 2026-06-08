const datasets = {
  municipal_2023_mayor: {
    label: "Municipal Mayor 2023",
    url: "/data/toronto_election_turnout/interpolation/map/municipal_2023_mayor_ct_map.geojson",
    officialRate: 0.3721,
    officialLabel: "Toronto official-elector rate",
    contextRate: 0.385,
    contextLabel: "Secondary reported Toronto rate"
  },
  provincial_2025: {
    label: "Provincial 2025",
    url: "/data/toronto_election_turnout/interpolation/map/provincial_2025_ct_map.geojson",
    officialRate: 0.4260,
    officialLabel: "Selected Toronto ridings",
    contextRate: 0.4522,
    contextLabel: "Ontario official"
  },
  federal_2025: {
    label: "Federal 2025",
    url: "/data/toronto_election_turnout/interpolation/map/federal_2025_ct_map.geojson",
    officialRate: 0.6501,
    officialLabel: "Selected Toronto ridings",
    contextRate: 0.691,
    contextLabel: "Ontario official"
  }
};

const metricConfig = {
  citizen: {
    label: "Votes / citizen population 18+",
    field: "estimated_participation_citizen_18plus",
    format: formatPct,
    breaks: [0.3, 0.4, 0.5, 0.6],
    labels: ["Under 30%", "30-40%", "40-50%", "50-60%", "60%+"]
  },
  electors: {
    label: "Votes / allocated electors",
    field: "estimated_turnout",
    format: formatPct,
    breaks: [0.3, 0.4, 0.5, 0.6],
    labels: ["Under 30%", "30-40%", "40-50%", "50-60%", "60%+"]
  }
};

const colors = ["#b23a48", "#e47d49", "#e9c46a", "#68a96b", "#277a66"];
const partyColors = ["#eef1ed", "#c8d8ce", "#91b7a1", "#559174", "#176b58"];
const state = {
  election: "municipal_2023_mayor",
  metric: "citizen",
  party: "",
  data: {},
  layer: null
};

const map = L.map("map", { preferCanvas: true, zoomControl: true })
  .setView([43.71, -79.38], 11);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const els = {
  election: document.getElementById("electionSelect"),
  metric: document.getElementById("metricSelect"),
  party: document.getElementById("partySelect"),
  distributionLabel: document.getElementById("distributionLabel"),
  partyNote: document.getElementById("partyNote"),
  count: document.getElementById("statCount"),
  votes: document.getElementById("statVotes"),
  citizen: document.getElementById("statCitizen"),
  official: document.getElementById("statOfficial"),
  comparisonRows: document.getElementById("comparisonRows"),
  comparisonNote: document.getElementById("comparisonNote"),
  legendTitle: document.getElementById("legendTitle"),
  legendRows: document.getElementById("legendRows"),
  status: document.getElementById("status")
};

function formatNumber(value, digits = 0) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "No data";
  return Number(value).toLocaleString("en-CA", { maximumFractionDigits: digits });
}

function formatPct(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "No data";
  return `${(Number(value) * 100).toFixed(1)}%`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function metricValue(properties) {
  if (state.party) {
    return state.election === "municipal_2023_mayor"
      ? candidateShare(properties, state.party)
      : partyShare(properties, state.party);
  }
  const value = properties[metricConfig[state.metric].field];
  return value === null || value === undefined ? null : Number(value);
}

function colorFor(value) {
  if (value === null || !Number.isFinite(value)) return "#d9ddd9";
  if (state.party) {
    const breaks = [0.1, 0.25, 0.4, 0.55];
    for (let index = 0; index < breaks.length; index += 1) {
      if (value < breaks[index]) return partyColors[index];
    }
    return partyColors[partyColors.length - 1];
  }
  const breaks = metricConfig[state.metric].breaks;
  for (let index = 0; index < breaks.length; index += 1) {
    if (value < breaks[index]) return colors[index];
  }
  return colors[colors.length - 1];
}

function styleFeature(feature) {
  return {
    color: "#ffffff",
    weight: 0.65,
    opacity: 0.9,
    fillColor: colorFor(metricValue(feature.properties)),
    fillOpacity: 0.82
  };
}

function readableParty(name) {
  return name
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace(/\bNdp New Democratic Party\b/g, "NDP-New Democratic Party")
    .replace(/\bPpc\b/g, "PPC")
    .replace(/\bPeople S Party PPC\b/g, "People's Party - PPC")
    .replace(/\bMarxist Leninist\b/g, "Marxist-Leninist");
}

function partyShare(properties, party) {
  const votes = Number((properties.party_votes || {})[party] || 0);
  const denominator = Number(properties.estimated_valid_candidate_votes || 0);
  return denominator > 0 ? votes / denominator : null;
}

function candidateShare(properties, candidate) {
  const votes = Number((properties.candidate_votes || {})[candidate] || 0);
  const denominator = Number(properties.estimated_valid_candidate_votes || 0);
  return denominator > 0 ? votes / denominator : null;
}

function partyRows(properties) {
  return Object.entries(properties.party_votes || {})
    .filter(([, value]) => Number(value) > 0)
    .sort((a, b) => Number(b[1]) - Number(a[1]))
    .map(([name, value]) => {
      const share = partyShare(properties, name);
      return `<tr><th>${escapeHtml(readableParty(name))}</th><td>${formatPct(share)} · ${formatNumber(value, 1)} votes</td></tr>`;
    })
    .join("");
}

function candidateRows(properties) {
  const denominator = Number(properties.estimated_valid_candidate_votes || 0);
  return (properties.top_candidates || [])
    .slice(0, 5)
    .map((row) => {
      const affiliation = state.election === "municipal_2023_mayor"
        ? ""
        : `<small>${escapeHtml(row.party_name)}</small>`;
      return `
        <tr>
          <th>${escapeHtml(row.candidate_name)}${affiliation}</th>
          <td>${formatPct(denominator > 0 ? row.estimated_votes / denominator : null)} · ${formatNumber(row.estimated_votes, 1)} votes</td>
        </tr>`;
    })
    .join("");
}

function detailHtml(properties, compact = false) {
  const candidates = candidateRows(properties);
  const parties = partyRows(properties);
  const quality = Number(properties.suppressed_da_count || 0) > 0
    ? `<p class="quality-note">Includes ${formatNumber(properties.suppressed_da_count)} suppressed DA overlap(s), weighted as zero.</p>`
    : "";
  return `
    <div class="${compact ? "hover-detail" : "popup"}">
      <p class="popup-kicker">Census tract</p>
      <h3>${escapeHtml(properties.ct_id)}</h3>
      <table>
        <tr><th>Total votes collected</th><td>${formatNumber(properties.estimated_total_votes, 1)}</td></tr>
        <tr><th>Valid candidate votes</th><td>${formatNumber(properties.estimated_valid_candidate_votes, 1)}</td></tr>
        <tr><th>Citizen population 18+</th><td>${formatNumber(properties.citizen_canadian_18over)}</td></tr>
        <tr><th>Turnout / citizen 18+</th><td>${formatPct(properties.estimated_participation_citizen_18plus)}</td></tr>
        <tr><th>Allocated-elector rate</th><td>${formatPct(properties.estimated_turnout)}</td></tr>
      </table>
      ${parties && state.election !== "municipal_2023_mayor" ? `<h4>Party share of valid votes</h4><table>${parties}</table>` : ""}
      ${candidates && state.election === "municipal_2023_mayor" ? `<h4>Leading candidate distribution</h4><table>${candidates}</table>` : ""}
      ${compact ? "" : quality}
    </div>`;
}

function updateLegend() {
  if (state.party) {
    const selectionLabel = state.election === "municipal_2023_mayor"
      ? state.party
      : readableParty(state.party);
    els.legendTitle.textContent = `${selectionLabel} vote share`;
    const labels = ["Under 10%", "10-25%", "25-40%", "40-55%", "55%+"];
    els.legendRows.innerHTML = labels.map((label, index) => `
      <div class="legend-row"><i style="background:${partyColors[index]}"></i><span>${label}</span></div>
    `).join("") + '<div class="legend-row"><i style="background:#d9ddd9"></i><span>No valid votes</span></div>';
    return;
  }
  const metric = metricConfig[state.metric];
  els.legendTitle.textContent = metric.label;
  els.legendRows.innerHTML = metric.labels.map((label, index) => `
    <div class="legend-row"><i style="background:${colors[index]}"></i><span>${label}</span></div>
  `).join("") + '<div class="legend-row"><i style="background:#d9ddd9"></i><span>No denominator</span></div>';
}

function updateStats(features) {
  const totals = features.reduce((result, feature) => {
    const p = feature.properties;
    result.votes += Number(p.estimated_total_votes || 0);
    result.electors += Number(p.estimated_electors || 0);
    result.citizens += Number(p.citizen_canadian_18over || 0);
    return result;
  }, { votes: 0, electors: 0, citizens: 0 });
  const config = datasets[state.election];
  els.count.textContent = formatNumber(features.length);
  els.votes.textContent = formatNumber(totals.votes);
  els.citizen.textContent = formatPct(totals.votes / totals.citizens);
  els.official.textContent = formatPct(totals.votes / totals.electors);
  els.comparisonRows.innerHTML = `
    <div><span>Citizen 18+ estimate</span><strong>${formatPct(totals.votes / totals.citizens)}</strong></div>
    <div><span>${config.officialLabel}</span><strong>${formatPct(config.officialRate)}</strong></div>
    <div><span>${config.contextLabel}</span><strong>${formatPct(config.contextRate)}</strong></div>`;
  els.comparisonNote.textContent = state.election === "municipal_2023_mayor"
    ? "The 38.5% value is a secondary Toronto report; the City final report rounds turnout to 37%."
    : "The broader Ontario rate is a context benchmark. It is not a direct validation target for selected Toronto ridings.";
}

function availableParties(features) {
  return Array.from(new Set(
    features.flatMap((feature) => Object.keys(feature.properties.party_votes || {}))
  )).filter((party) => party !== "non_partisan")
    .sort((a, b) => readableParty(a).localeCompare(readableParty(b)));
}

function availableCandidates(features) {
  return Array.from(new Set(
    features.flatMap((feature) => Object.keys(feature.properties.candidate_votes || {}))
  )).sort((a, b) => a.localeCompare(b));
}

function updatePartyOptions(features) {
  if (state.election === "municipal_2023_mayor") {
    const candidates = availableCandidates(features);
    els.distributionLabel.textContent = "Mayoral candidate";
    els.party.innerHTML = '<option value="">Turnout map</option>' +
      candidates.map((candidate) => `<option value="${escapeHtml(candidate)}">${escapeHtml(candidate)}</option>`).join("");
    els.party.disabled = false;
    state.party = "";
    els.partyNote.textContent = "Toronto mayoral ballots have no party labels. Select a candidate to map their share of valid votes.";
    return;
  }
  const parties = availableParties(features);
  els.distributionLabel.textContent = "Political party";
  els.party.innerHTML = '<option value="">Turnout map</option>' +
    parties.map((party) => `<option value="${escapeHtml(party)}">${escapeHtml(readableParty(party))}</option>`).join("");
  els.party.disabled = false;
  state.party = "";
  els.partyNote.textContent = "Selecting a party colors CTs by vote share; hover also reports its estimated votes.";
}

function draw() {
  const collection = state.data[state.election];
  if (state.layer) state.layer.remove();
  state.layer = L.geoJSON(collection, {
    style: styleFeature,
    onEachFeature(feature, layer) {
      layer.bindPopup(detailHtml(feature.properties), { maxWidth: 430 });
      layer.bindTooltip(detailHtml(feature.properties, true), {
        sticky: true,
        direction: "auto",
        className: "ct-hover-tooltip",
        maxWidth: 420
      });
      layer.on({
        mouseover(event) {
          event.target.setStyle({ weight: 2, color: "#16251e", fillOpacity: 0.94 });
          event.target.bringToFront();
        },
        mouseout(event) {
          state.layer.resetStyle(event.target);
        }
      });
    }
  }).addTo(map);
  updateStats(collection.features);
  updateLegend();
  els.status.textContent = state.party
    ? `${datasets[state.election].label}: ${
        state.election === "municipal_2023_mayor"
          ? state.party
          : readableParty(state.party)
      } vote share across 585 CTs`
    : `${datasets[state.election].label}: 585 validated census tract estimates`;
  map.fitBounds(state.layer.getBounds(), { padding: [18, 18] });
}

async function loadElection(key) {
  if (!state.data[key]) {
    els.status.textContent = `Loading ${datasets[key].label}...`;
    const response = await fetch(datasets[key].url);
    if (!response.ok) throw new Error(`Could not load ${datasets[key].label}`);
    state.data[key] = await response.json();
  }
  state.election = key;
  updatePartyOptions(state.data[key].features);
  draw();
}

els.election.addEventListener("change", (event) => {
  loadElection(event.target.value).catch((error) => {
    els.status.textContent = error.message;
    console.error(error);
  });
});

els.metric.addEventListener("change", (event) => {
  state.metric = event.target.value;
  draw();
});

els.party.addEventListener("change", (event) => {
  state.party = event.target.value;
  els.metric.disabled = Boolean(state.party);
  draw();
});

let resizeTimer;
window.addEventListener("resize", () => {
  window.clearTimeout(resizeTimer);
  resizeTimer = window.setTimeout(() => {
    map.invalidateSize();
    if (state.layer) {
      map.fitBounds(state.layer.getBounds(), { padding: [18, 18] });
    }
  }, 120);
});

loadElection(state.election).catch((error) => {
  els.status.textContent = error.message;
  console.error(error);
});
