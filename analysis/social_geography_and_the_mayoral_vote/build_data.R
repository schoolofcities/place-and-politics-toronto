# Build the static data files for the web app (docs/data/).
# Run from the project root:  Rscript prep/build_data.R

suppressPackageStartupMessages({
  library(sf)
  library(foreign)
  library(haven)
  library(dplyr)
  library(tidyr)
  library(arrow)
  library(jsonlite)
  library(rmapshaper)
})

# Census inputs come from the book's census construction project, which is read
# but never modified here. `longbytime_harm6` is the table produced just before
# that pipeline standardizes and drops the counts, so it still holds the
# absolute counts and the nominal values of the continuous variables.
book <- path.expand("~/Dropbox (Personal)/Western Research/Projects/Place and Politics Book")
census_rdata <- file.path(book, "1_data_toronto/10 census data construction/.RData")
geog_dbf <- file.path(book, "3_spatial/2_ct2021_toronto/ct2021tor_city_wards_neigh_ctrd.dbf")

out <- "docs/data"
dir.create(out, recursive = TRUE, showWarnings = FALSE)

fmt_id <- function(x) sprintf("%.2f", as.numeric(x))

# ---- Boundaries and tract geography ----------------------------------------
geog <- read.dbf(geog_dbf, as.is = TRUE) |>
  transmute(ct = fmt_id(geosid),
            ward = wards25,
            wardname = wards25nm,
            # the dbf truncates field values at 10 characters
            oldcity = ifelse(oldcity == "Scarboroug", "Scarborough", oldcity),
            nname = nname)

tracts <- st_read("ct2021tor.shp", quiet = TRUE) |>
  st_transform(4326) |>
  transmute(ct = fmt_id(ctuid2021), name = geoname) |>
  left_join(geog, by = "ct") |>
  ms_simplify(keep = 0.35, keep_shapes = TRUE)

stopifnot(!any(is.na(tracts$wardname)), !any(is.na(tracts$nname)))

st_write(tracts, file.path(out, "tracts.geojson"),
         layer_options = c("COORDINATE_PRECISION=5", "RFC7946=YES"),
         delete_dsn = TRUE, quiet = TRUE)

# ---- Census variables -------------------------------------------------------
ce <- new.env()
load(census_rdata, envir = ce)
h6 <- as.data.frame(get("longbytime_harm6", ce))  # shares, counts, nominal values
# Walk Score, Transit Score and Bike Score are proprietary (Walk Score / Redfin) and
# aren't licensed for republication, so they're left out of the published data.
h6 <- h6[, !grepl("score$", names(h6))]
vcoded <- get("variables_coded", ce)              # source t_code -> published name
apportioned <- get("out", ce)                     # long tables, carry t_denom

# Standardize the continuous variables the same way the census pipeline does:
# z-scores within each census year. Reproduces the s_* variables in the .dta.
q_vars <- unique(c(grep("__nc$", names(h6), value = TRUE),
                   grep("^pmi_prox_", names(h6), value = TRUE)))

census <- h6 |>
  mutate(ct = fmt_id(geosid), year = as.integer(time)) |>
  group_by(year) |>
  mutate(across(all_of(q_vars),
                ~ (.x - mean(.x, na.rm = TRUE)) / sd(.x, na.rm = TRUE),
                .names = "s_{.col}")) |>
  ungroup()

# Denominator of each share: the pipeline builds shares as count / table total
# but drops the totals when it recodes, so recover them as count / share.
# Variables of one theme usually share a total, but not always (education, for
# instance, mixes a 15-and-over table with a 25-to-64 one), so variables are
# grouped by theme and then split whenever their totals disagree.
denom_map <- lapply(apportioned, \(o) distinct(as.data.frame(o)[, c("t_code", "t_denom")])) |>
  bind_rows() |>
  distinct() |>
  filter(t_denom != "noncount")

pct_ids <- grep("_pct$", names(census), value = TRUE)

denom_group <- function(id) {
  src <- sub("_pct$", "", vcoded$t_code[vcoded$coded == id])
  d <- sort(unique(denom_map$t_denom[denom_map$t_code %in% src]))
  if (!length(d)) return(NA_character_)
  d <- d[1]                            # occupation and education vary by year
  if (grepl("^oc\\d\\d_tot$", d)) "occ__tot" else if (grepl("^edc", d)) "edca_tot" else d
}

pct_denom <- vapply(pct_ids, denom_group, "")

# Total implied by one variable, where its share is non-zero
implied_total <- function(v) {
  share <- census[[v]]
  ifelse(!is.na(share) & share > 0, census[[sub("_pct$", "_abs", v)]] / share, NA_real_)
}

agrees <- function(a, b) {
  ok <- !is.na(a) & !is.na(b) & pmax(a, b) > 0
  !any(ok) || max(abs(a[ok] - b[ok]) / pmax(a[ok], b[ok])) < 1e-3
}

pct_den_col <- setNames(character(length(pct_ids)), pct_ids)
den_cols <- list()

for (g in unique(na.omit(pct_denom))) {
  for (v in pct_ids[which(pct_denom == g)]) {
    est <- implied_total(v)
    existing <- if (is.null(names(den_cols))) character(0) else names(den_cols)
    in_group <- existing[startsWith(existing, paste0("den_", g))]
    match_col <- Find(\(cl) agrees(est, den_cols[[cl]]), in_group)
    if (is.null(match_col)) {
      match_col <- paste0("den_", g, if (length(in_group)) length(in_group) + 1L else "")
      den_cols[[match_col]] <- est
    } else {
      # fill gaps left where this variable's share is zero
      den_cols[[match_col]] <- coalesce(den_cols[[match_col]], est)
    }
    pct_den_col[v] <- match_col
  }
}

for (cl in names(den_cols)) census[[cl]] <- den_cols[[cl]]

# % visible minority is the complement of % white
census$vminvisi_pct <- 1 - census$vminnvis_pct
census$vminvisi_abs <- census[[pct_den_col["vminnvis_pct"]]] - census$vminnvis_abs
pct_den_col["vminvisi_pct"] <- pct_den_col["vminnvis_pct"]
pct_denom["vminvisi_pct"] <- pct_denom["vminnvis_pct"]

lookup <- read.csv("tor_varname_lookup.csv", fileEncoding = "UTF-8-BOM")
curated_ids <- lookup$variable[lookup$keep == 1]

# Labels for variables missing from (or mislabelled in) the lookup table
extra_labels <- c(
  abidabor__ne_pct = "% Indigenous identity (n.e.c.)",
  abidabor1resfina_pct = "% First Nations",
  abidabor1resinuk_pct = "% Inuk",
  abidabor1resmeti_pct = "% Métis",
  abidabormres_pct = "% Multiple Indigenous identities",
  abidnabo_pct = "% Non-Indigenous",
  dwtpatch_pct = "% Attached Housing",
  edcacert_pct = "% College / Trades Certificate",
  edcauniv_pct = "% University Degree",
  ethmasiaeastchin_pct = "% Chinese Origin",
  ethmasiasoutinda_pct = "% East Indian Origin",
  ethmasiasoutpaks_pct = "% Pakistani Origin",
  ethmasiawestleba_pct = "% Lebanese Origin",
  ethmcarihait_pct = "% Haitian Origin",
  ethmeurobritengl_pct = "% English Origin",
  ethmeurobritiris_pct = "% Irish Origin",
  ethmeurobritscot_pct = "% Scottish Origin",
  ethmeuroeastpoli_pct = "% Polish Origin",
  ethmeuroeastukra_pct = "% Ukrainian Origin",
  ethmeurofren_tot_pct = "% French Origin",
  ethmeurosoutgrek_pct = "% Greek Origin",
  lfaainlfempl_pct = "% Employed",
  lfaanolf_pct = "% Not in Labour Force",
  lnmt1resoffifr___pct = "% French Mother Tongue",
  vminvisiweas_pct = "% West Asian",
  vminvisi_pct = "% Visible Minority",
  # Non-percentage variables: z-scores standardized within each census year
  s_ihat_avg__nc = "Avg. Household Income",
  s_ihat_med__nc = "Median Household Income",
  s_iit__avg__nc = "Avg. Individual Income",
  s_iit__med__nc = "Median Individual Income",
  s_popdsqkm__nc = "Population Density",
  s_dist__nc = "Distance from City Hall",
  s_pmi_prox_idx_emp = "Proximity to Jobs",
  s_pmi_prox_idx_pharma = "Proximity to Pharmacy",
  s_pmi_prox_idx_childcare = "Proximity to Childcare",
  s_pmi_prox_idx_health = "Proximity to Health Care",
  s_pmi_prox_idx_grocery = "Proximity to Grocery",
  s_pmi_prox_idx_educpri = "Proximity to Elementary School",
  s_pmi_prox_idx_educsec = "Proximity to Secondary School",
  s_pmi_prox_idx_lib = "Proximity to Library",
  s_pmi_prox_idx_parks = "Proximity to Parks",
  s_pmi_prox_idx_transit = "Proximity to Transit"
)

std_vars <- grep("^s_", names(extra_labels), value = TRUE)
pct_vars <- setdiff(grep("_pct$", names(census), value = TRUE), "hhtnband_pct")
map_vars <- c(pct_vars, std_vars)

group_of <- function(v) {
  case_when(
    grepl("^s_i", v) ~ "Income",
    grepl("^s_", v) ~ "Density, Location & Access",
    grepl("^agec|^mars", v) ~ "Age & Family",
    grepl("^abid|^vmin", v) ~ "Visible Minority & Indigenous Identity",
    grepl("^ethm", v) ~ "Ethnic Origin",
    grepl("^imst|^lnmt", v) ~ "Immigration & Language",
    grepl("^rlgn", v) ~ "Religion",
    grepl("^edca|^lfaa", v) ~ "Education & Labour Force",
    grepl("^occ", v) ~ "Occupation",
    grepl("^dw|^hhtn", v) ~ "Housing",
    grepl("^jwmd", v) ~ "Commuting",
    TRUE ~ "Other"
  )
}

# Curated set: lookup keep == 1, substitutes for lookup vars not in the data,
# and all income measures.
curated <- union(curated_ids, c("edcauniv_pct", "vminvisi_pct",
                                "s_ihat_avg__nc", "s_ihat_med__nc",
                                "s_iit__avg__nc", "s_iit__med__nc",
                                "s_popdsqkm__nc", "s_dist__nc",
                                "s_pmi_prox_idx_emp", "s_pmi_prox_idx_grocery",
                                "s_pmi_prox_idx_childcare"))

label_of <- function(v) {
  lab <- extra_labels[v]
  from_lookup <- lookup$varname[match(v, lookup$variable)]
  ifelse(is.na(lab), from_lookup, lab) |> unname()
}

# Labels for the table totals the shares are calculated against
denom_labels <- c(lfaa_tot = "Labour Force Status - Total",
                  abid_tot = "Indigenous Identity - Total",
                  setNames(lookup$varname[grepl("_tot$", lookup$variable)],
                           lookup$variable[grepl("_tot$", lookup$variable)]))

# Units of the nominal (unstandardized) values behind each z-score
nominal_units <- c(ihat_avg__nc = "dollars", ihat_med__nc = "dollars",
                   iit__avg__nc = "dollars", iit__med__nc = "dollars",
                   popdsqkm__nc = "per_km2", dist__nc = "km")

vars_meta <- tibble(id = map_vars) |>
  mutate(label = label_of(id),
         group = group_of(id),
         kind = ifelse(id %in% std_vars, "z", "pct"),
         curated = id %in% curated,
         # column holding the count, and the table total it is a share of
         num = ifelse(kind == "pct", sub("_pct$", "_abs", id), NA_character_),
         den = ifelse(kind == "pct", unname(pct_den_col[id]), NA_character_),
         den_label = unname(denom_labels[pct_denom[id]]),
         # column holding the nominal value behind the z-score, and its units
         nom = ifelse(kind == "z", sub("^s_", "", id), NA_character_),
         unit = ifelse(kind == "z", coalesce(unname(nominal_units[nom]), "index"),
                       NA_character_)) |>
  filter(!is.na(label)) |>
  # Drop variables with no data at all
  filter(sapply(id, function(v) any(!is.na(census[[v]])))) |>
  arrange(group, label)

# Years in which each variable is available
vars_meta$years <- lapply(vars_meta$id, function(v)
  sort(unique(census$year[!is.na(census[[v]])])))

# Proximity measures and distance from City Hall are
# measured once and repeated for every census year. (Their z-scores wobble in
# the third decimal because each year standardizes over a slightly different
# set of tracts, so test the nominal value.)
vars_meta$fixed_in_time <- vapply(seq_len(nrow(vars_meta)), function(k) {
  col <- if (vars_meta$kind[k] == "z") vars_meta$nom[k] else vars_meta$id[k]
  n <- tapply(round(census[[col]], 4), census$ct, \(x) length(unique(na.omit(x))))
  all(n <= 1)
}, logical(1))

stopifnot(all(na.omit(vars_meta$num) %in% names(census)),
          all(na.omit(vars_meta$den) %in% names(census)),
          all(na.omit(vars_meta$nom) %in% names(census)),
          !any(is.na(vars_meta$den_label[vars_meta$kind == "pct"])))

# Distance from City Hall reads better in kilometres than metres
census$dist__nc <- census$dist__nc / 1000

value_cols <- c(vars_meta$id, na.omit(unique(c(vars_meta$num, vars_meta$den, vars_meta$nom))))

census_out <- census |>
  select(ct, year, all_of(value_cols)) |>
  mutate(across(all_of(value_cols), ~ round(.x, 4)))

census_schema <- schema(c(list(ct = utf8(), year = int32()),
                          setNames(rep(list(float32()), length(value_cols)),
                                   value_cols)))
census_out <- arrow_table(census_out, schema = census_schema)

write_parquet(census_out, file.path(out, "census.parquet"),
              compression = "snappy")

# ---- Elections --------------------------------------------------------------
elec <- read_dta("tor_electoral_ct2021_pct.dta") |> zap_labels()
elec$ct <- fmt_id(elec$ctuid2021)

pct_cols <- grep("^pct.+\\d{4}$", names(elec), value = TRUE)
elec_long <- elec |>
  select(ct, all_of(pct_cols)) |>
  pivot_longer(-ct, names_to = "col", values_to = "share") |>
  mutate(year = as.integer(sub(".*(\\d{4})$", "\\1", col)),
         candidate = sub("^pct(.+)\\d{4}$", "\\1", col)) |>
  filter(candidate != "pop")          # pctpop2006 is population, not a candidate

# Citywide shares from the city* total columns
city <- elec_long |>
  distinct(col, year, candidate) |>
  mutate(votes = sapply(paste0("city", candidate, year),
                        function(v) if (v %in% names(elec)) elec[[v]][1] else NA_real_)) |>
  group_by(year) |>
  mutate(city_share = votes / sum(votes, na.rm = TRUE)) |>
  ungroup()

# Full names for candidates above the 1% threshold; anything else falls back
# to a name built from the column ("bailao_ana" -> "Ana Bailao").
full_names <- c(
  lastman = "Mel Lastman", hall = "Barbara Hall", gomberg = "Tooker Gomberg",
  anderson = "Enza Anderson", miller = "David Miller", tory = "John Tory",
  tory_john = "John Tory", nunziata = "John Nunziata",
  pitfield = "Jane Pitfield", ledrew = "Stephen LeDrew", ford = NA,
  smitherman = "George Smitherman", pantalone = "Joe Pantalone",
  chow = "Olivia Chow", chow_olivia = "Olivia Chow",
  keesmaat = "Jennifer Keesmaat", goldy = "Faith Goldy",
  gebresellassi = "Saron Gebresellassi", penalosa_gil = "Gil Pe\u00f1alosa",
  brown_chloe_marie = "Chloe Brown", brown_chloe = "Chloe Brown",
  acton_blake = "Blake Acton", climenhaga_sarah = "Sarah Climenhaga",
  luk_tony = "Tony Luk", yan_jack = "Jack Yan", bailao_ana = "Ana Bail\u00e3o",
  saunders_mark = "Mark Saunders", furey_anthony = "Anthony Furey",
  matlow_josh = "Josh Matlow", hunter_mitzie = "Mitzie Hunter",
  saccoccia_chris = "Chris Saccoccia", bradford_brad = "Brad Bradford",
  other = "All other candidates"
)

cand_label <- function(candidate, year) {
  lab <- unname(full_names[candidate])
  lab[candidate == "ford"] <- ifelse(year[candidate == "ford"] == 2010,
                                     "Rob Ford", "Doug Ford")
  auto <- vapply(strsplit(candidate, "_"), function(p) {
    p <- tools::toTitleCase(p)
    paste(c(p[-1], p[1]), collapse = " ")
  }, "")
  ifelse(is.na(lab), auto, lab)
}

# Keep candidates with >= 1% citywide, plus the "other" category
keep_cands <- city |>
  filter(city_share >= 0.01 | candidate == "other") |>
  mutate(label = cand_label(candidate, year)) |>
  arrange(year, candidate == "other", desc(city_share))

# Votes cast for each candidate (a_*). Counts are apportioned to 2021 tracts,
# so early years are fractional.
votes_long <- elec |>
  select(ct, matches("^a_.+\\d{4}$")) |>
  pivot_longer(-ct, names_to = "col", values_to = "votes") |>
  mutate(year = as.integer(sub(".*(\\d{4})$", "\\1", col)),
         candidate = sub("^a_(.+)\\d{4}$", "\\1", col)) |>
  filter(candidate != "pop") |>
  select(ct, year, candidate, votes)

elec_out <- elec_long |>
  semi_join(keep_cands, by = c("year", "candidate")) |>
  left_join(votes_long, by = c("ct", "year", "candidate")) |>
  transmute(ct, year, candidate, share = round(share, 4), votes = round(votes, 1)) |>
  arrow_table(schema = schema(ct = utf8(), year = int32(), candidate = utf8(),
                              share = float32(), votes = float32()))

write_parquet(elec_out, file.path(out, "elections.parquet"),
              compression = "snappy")

# Denominators per tract and election: total votes cast and eligible voters
# (eligible voters are not in the file for 2022 and 2023).
years <- sort(unique(keep_cands$year))
turnout <- lapply(years, function(y) {
  elig <- paste0("e_elig", y)
  tibble(ct = elec$ct, year = as.integer(y),
         votes_cast = round(elec[[paste0("voted", y)]], 1),
         eligible = if (elig %in% names(elec)) round(elec[[elig]], 1) else NA_real_)
}) |> bind_rows()

write_parquet(arrow_table(turnout, schema = schema(
                ct = utf8(), year = int32(),
                votes_cast = float32(), eligible = float32())),
              file.path(out, "turnout.parquet"), compression = "snappy")

city_totals <- turnout |>
  group_by(year) |>
  summarise(votes_cast = sum(votes_cast, na.rm = TRUE),
            eligible = if (all(is.na(eligible))) NA_real_ else sum(eligible, na.rm = TRUE))

elections_meta <- keep_cands |>
  group_by(year) |>
  group_map(~ list(year = .y$year,
                   city_votes_cast = round(city_totals$votes_cast[city_totals$year == .y$year]),
                   city_eligible = round(city_totals$eligible[city_totals$year == .y$year]),
                   candidates = lapply(seq_len(nrow(.x)), function(i)
                     list(id = .x$candidate[i], label = .x$label[i],
                          city_share = round(.x$city_share[i], 4),
                          city_votes = round(.x$votes[i])))))

write_json(list(census_years = sort(unique(census$year)),
                variables = vars_meta,
                elections = elections_meta),
           file.path(out, "meta.json"), auto_unbox = TRUE, pretty = TRUE, na = "null")

message("Wrote ", paste(list.files(out), collapse = ", "))
