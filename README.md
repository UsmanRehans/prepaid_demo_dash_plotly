# ISP Prepaid Pricing Dashboard

An interactive dashboard for analyzing ISP prepaid pricing across locations and carriers.

**Author:** Usman Rehan

## Features

- Interactive map — click any location to drill into pricing
- Carrier filter (AT&T Fiber, Spectrum, Verizon Fios)
- Price trend line chart by location over time
- Sortable and filterable data table

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open [http://localhost:8050](http://localhost:8050)

## Data

Place `isp_pricing_data.csv` in the root directory before running.

| Column | Description |
|---|---|
| `pr__vendor` | Carrier name |
| `price` | Monthly price ($) |
| `location_lat` | Latitude |
| `location_long` | Longitude |
| `location_zip` | ZIP code |
| `location_census_block` | Census Block FIPS |
| `location_address` | Street address |
| `date` | Date (YYYY-MM-DD) |
