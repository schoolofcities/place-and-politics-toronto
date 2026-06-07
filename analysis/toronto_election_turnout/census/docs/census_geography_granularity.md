# Census Geography Granularity

## Finding

The Toronto DA layer is substantially finer than the ADA layer:

- DA: 3,743 verified Toronto profile areas; median land area 0.095 km².
- CT: 622 stored Toronto-clipped features; median land area 0.788 km².
- ADA: 279 areas; median land area 1.792 km².

An ADA contains 13.4 Toronto DAs on average, with a range from 1 to 46.

## Official Hierarchy

Statistics Canada defines an ADA as a grouping of existing dissemination
geographies. In census metropolitan areas with census tracts, including
Toronto, adjacent CTs are the ADA building units. Statistics Canada also
requires DAs to respect CT boundaries.

Therefore, the project uses:

```text
DA -> CT -> ADA
```

Official definitions:

- Aggregate dissemination area:
  https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo053
- Dissemination area:
  https://www12.statcan.gc.ca/census-recensement/2021/ref/dict/az/definition-eng.cfm?ID=geo021
- 2021 Census boundary files:
  https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21

## Crosswalk Method

The builder places an interior point within each verified Toronto DA and
identifies the containing CT and ADA. This avoids false matches caused by
boundaries merely touching.

All 3,743 Toronto DA profile identifiers receive one CT and one ADA.

The raw clipped DA geometry contains 3,807 features because its original
spatial extraction includes edge features outside the verified Toronto profile
universe. Those extras are excluded from the map-ready DA output.

## DA-to-ADA Count Check

The DA-level Canadian-citizen-aged-18+ estimates sum to 1,869,930. The
independently published ADA profile values sum to 1,870,025.

The 95-person citywide difference is retained and documented. Census Profile
counts are independently rounded and may be suppressed, so exact aggregation
across published geography levels is not expected.

## Suppressed Citizenship Values

Sixteen Toronto DAs have no published value for `Canadian citizens aged 18 and
over`. Their fourth data-quality-flag digit is `9`, which Statistics Canada
defines as long-form data suppressed to meet the confidentiality requirements
of the Statistics Act.

The same DAs also have suppressed values for the total citizenship universe,
Canadian citizens, Canadian citizens aged under 18, men+ and women+
components, and not-Canadian citizens. The 18+ value therefore cannot be
calculated exactly from other published citizenship cells.

These rows remain null. This is distinct from a zero value, census
non-completion, or a mapping error.
