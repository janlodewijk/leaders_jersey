from procyclingstats import RaceStartlist

def extract_startlist(race, year):
    url = f"https://www.procyclingstats.com/race/{race}/{year}/startlist"
    startlist = RaceStartlist(url)
    return startlist.parse()
