from procyclingstats import RaceStartlist
from etl.logging_config import logger

def extract_startlist(race, year):
    try:
        url = f"https://www.procyclingstats.com/race/{race}/{year}/startlist"
        startlist = RaceStartlist(url)
        data = startlist.parse()

        # Expecting structure: {'startlist': [...]}
        if not isinstance(data, dict) or 'startlist' not in data:
            raise ValueError(f"Expected dict with 'startlist', got: {type(data)} - keys: {list(data.keys())}")

        logger.info(f"Startlist successfully extracted for {race} ({year}) with {len(data['startlist'])} riders")

        return {
            "race": race,
            "year": year,
            "startlist": data["startlist"]
        }

    except Exception as e:
        logger.error(f"Something went wrong while extracting data for {race} ({year}): {e}")
        return None
