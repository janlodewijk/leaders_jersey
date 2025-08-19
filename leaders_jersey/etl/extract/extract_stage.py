from procyclingstats import Stage
from etl.logging_config import logger
import pandas as pd


def extract_stage_info(race, year):
    stages_info = []
    stage_number = 1
    max_stages = 30

    logger.info(f"Starting stage info extraction for {race} ({year})")

    # Check if there is a prologue (procyclingstats usually considers the stage after the prologue as stage 1)
    prologue_url = f"https://www.procyclingstats.com/race/{race}/{year}/prologue"
    try:
        prologue = Stage(prologue_url)

        stages_info.append({
            'race': race,
            'year': year,
            'stage_number': 0,
            'stage_date': prologue.date(),
            'departure': prologue.departure(),
            'arrival': prologue.arrival(),
            'distance': round(prologue.distance())
        })
        logger.info(f"Extracted prologue: {prologue.departure()} → {prologue.arrival()}, {prologue.distance()} km")
    except Exception as e:
        logger.info(f"No prologue found for {race} ({year})")

    while stage_number <= max_stages:
        
        try:
            url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
            stage_info_raw = Stage(url)

            try:
                date = stage_info_raw.date()
                departure = stage_info_raw.departure()
                arrival = stage_info_raw.arrival()
                distance = stage_info_raw.distance()
            except Exception as e:
                logger.warning(f"Failed to parse stage {stage_number} ({url}): {e}")
                break
        
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
            

from procyclingstats import Stage
from etl.logging_config import logger

def extract_stage_results(race, year, stage_number):
    try:
        if stage_number == 0:
            url = f"https://www.procyclingstats.com/race/{race}/{year}/prologue"
        else:
            url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"

        stage = Stage(url)
        raw_data = stage._raw_results  # This avoids .parse(), which is too strict

        if not isinstance(raw_data, dict):
            logger.error(f"Unexpected result format for {race} {year} stage {stage_number}")
            return None

        cleaned_data = {}

        for key in ['results', 'gc']:
            entries = raw_data.get(key, [])
            cleaned_entries = []

            for rider in entries:
                valid = True

                for time_field in ['time', 'bonus']:
                    if time_field in rider and isinstance(rider[time_field], str):
                        if '*' in rider[time_field] or any(c.isalpha() for c in rider[time_field]):
                            logger.warning(f"⛔ Skipping rider due to bad {time_field}: {rider.get('rider_name')} — value: {rider[time_field]}")
                            valid = False
                            break

                if valid:
                    cleaned_entries.append(rider)

            cleaned_data[key] = cleaned_entries

        logger.info(f"✅ Extracted cleaned results for {race} ({year}) - stage {stage_number}")
        return cleaned_data

    except Exception as e:
        logger.error(f"❌ Failed to extract results for {race} {year} stage {stage_number}: {e}")
        return None
