from ..extract.extract_startlist import extract_startlist
from ..transform.transform_startlist import transform_startlist

# Run this script in the terminal: python -m etl.scripts.run_etl


race = "tour-de-france"
year = 2025

raw_startlist = extract_startlist(race, year)

startlist_df = transform_startlist(raw_startlist)

print(startlist_df.head())