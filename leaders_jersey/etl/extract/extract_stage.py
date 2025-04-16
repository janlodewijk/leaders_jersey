from procyclingstats import Stage
from etl.logging_config import logger


def extract_stage_info(race, year):
    stages_info = []
    stage_number = 1
    max_stages = 30

    logger.info(f"Starting stage info extraction for {race} ({year})")

    while stage_number <= max_stages:
        
        try:
            url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
            stage_info_raw = Stage(url)

            date = stage_info_raw.date()
            departure = stage_info_raw.departure()
            arrival = stage_info_raw.arrival()
            distance = stage_info_raw.distance()

        
            stage_info = {
                'race': race,
                'year': year,
                'stage_number': stage_number,
                'stage_date': date,
                'departure': departure,
                'arrival': arrival,
                'distance': round(distance)
            }

            stages_info.append(stage_info)
            logger.info(f"✅ Extracted stage {stage_number}: {departure} → {arrival}, {distance} km")
            stage_number += 1

        except Exception as e:
            logger.warning(f"Stopped extracting at stage {stage_number} Reason: {e}")
            break
    
    logger.info(f"Finished extraction: {len(stages_info)} stages found for {race} ({year})")
    return stages_info
            
    


def extract_stage_results(race, year, stage_number):
    try:
        url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
        stage_results_raw = Stage(url)

        parsed_results = stage_results_raw.parse()
        logger.info(f"Sucessfully extracted results for {race} ({year}) - stage {stage_number}")
        return parsed_results
    
    except Exception as e:
        logger.error(f"Stage {stage_number} not finished / no results yet. Error: {e}")
        return None