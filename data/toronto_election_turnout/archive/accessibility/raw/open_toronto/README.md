# Open Toronto Raw Accessibility Inputs

The full Open Toronto address-point CSV is not committed because it is larger
than GitHub's normal file-size limit.

To reproduce the local raw-data state, download the Address Points dataset from:

- https://open.toronto.ca/dataset/address-points/

Place the downloaded CSV here:

- `data/toronto_election_turnout/accessibility/raw/open_toronto/address_points.csv`

The accessibility scripts use this file as a local address-point reference for
polling-location geocoding and label matching.
