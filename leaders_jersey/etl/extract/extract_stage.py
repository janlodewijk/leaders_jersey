from procyclingstats import Stage
from datetime import date, datetime

def extract_stage_info(race, year, stage_number):
    url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
    stage_info_raw = Stage(url)
    
    try:
        date = stage_info_raw.date()
        departure = stage_info_raw.departure()
        arrival = stage_info_raw.arrival()
        distance = stage_info_raw.distance()
    except Exception as e:
        print(f"Error scraping stage {stage_number}: {e}")
    
    stage_info = {
        'date': date,
        'departure': departure,
        'arrival': arrival,
        'distance': distance
    }

    return stage_info


def extract_stage_results(race, year, stage_number):
    url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
    stage_results_raw = Stage(url)

    try:
        parsed_results = stage_results_raw.parse()
        return parsed_results
    
    except Exception as e:
        print(f"Stage {stage_number} not finished / no results yet. Error: {e}")
        return None
    


print(extract_stage_results("tour-de-france", 2025, 1))