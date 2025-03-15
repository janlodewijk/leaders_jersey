from etl.extract.extract_startlist import extract_startlist

race = "tour-de-france"
year = 2025

tdf_startlist = extract_startlist(race, year)

print(tdf_startlist)