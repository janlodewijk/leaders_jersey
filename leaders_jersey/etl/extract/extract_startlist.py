from procyclingstats import RaceStartlist
from etl.logging_config import logger

def extract_startlist(race, year):
    try:
        url = f"https://www.procyclingstats.com/race/{race}/{year}/startlist"
        startlist = RaceStartlist(url)
        data = startlist.parse()
        logger.info(f"Startlist successfully extracted for {race} ({year}) with {len(data)} riders")
        return data
    except Exception as e:
        logger.error(f"Something went wrong while extrcting data for {race} ({year}): {e}")
        return None
