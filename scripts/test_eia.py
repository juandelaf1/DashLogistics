import requests

API_KEY = "QO7Z7RK9NRLOkbWrYsIWg9wgvo8Q6oor6R0hTaR7"
BASE = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

# Get US regular gasoline price (latest)
r = requests.get(BASE,
    params={
        "api_key": API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[duoarea][]": "NUS",
        "facets[product][]": "EPM0R",  # Regular gasoline
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    },
    timeout=10)
if r.status_code == 200 and r.json()["response"]["data"]:
    row = r.json()["response"]["data"][0]
    print(f"US Regular: ${row['value']}/gal on {row['period']}")
else:
    print(f"US Regular: {r.status_code} - no data or error")

# US diesel
r = requests.get(BASE,
    params={
        "api_key": API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[duoarea][]": "NUS",
        "facets[product][]": "EPD2D",  # Diesel
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,
    },
    timeout=10)
if r.status_code == 200 and r.json()["response"]["data"]:
    row = r.json()["response"]["data"][0]
    print(f"US Diesel: ${row['value']}/gal on {row['period']}")
else:
    print(f"US Diesel: {r.status_code}")

# Try getting all unique duoarea values for a sample
r = requests.get(BASE,
    params={
        "api_key": API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[product][]": "EPM0R",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 100,
    },
    timeout=10)
if r.status_code == 200:
    areas = set()
    for row in r.json()["response"]["data"]:
        areas.add((row["duoarea"], row["area-name"]))
    print(f"\nAreas with regular gas data ({len(areas)}):")
    for code, name in sorted(areas)[:20]:
        print(f"  {code}: {name}")
