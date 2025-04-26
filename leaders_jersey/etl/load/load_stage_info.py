import pandas as pd
from game.models import Race, Stage, Rider, StageResult
from datetime import timedelta
from etl.logging_config import logger


def load_stage_info(transformed_stage_info):
    try:
        for index, row in transformed_stage_info.iterrows():
            race = row['race']
            year = row['year']
            stage_number = row['stage_number']
            stage_date = row['stage_date']
            departure = row['departure']
            arrival = row['arrival']
            distance = row['distance']
            stage_type = row['stage_type']

            # Get the Race object using url_reference and year
            try:
                race_obj = Race.objects.get(url_reference=race, year=year)
            
            except Race.DoesNotExist:
                logger.warning(f"Race not found for {race} {year}. Skipping stage {stage_number}")
                continue

            
            # Get or create the Stage
            stage_obj, created = Stage.objects.get_or_create(
                race = race_obj,
                stage_number=stage_number,
                defaults={
                    'stage_date': stage_date,
                    'departure': departure,
                    'arrival': arrival,
                    'distance': distance,
                    'stage_type': stage_type
                }
            )

            # If stage exists, update fields
            if not created:
                stage_obj.stage_date = stage_date
                stage_obj.departure = departure
                stage_obj.arrival = arrival
                stage_obj.distance = distance
                stage_obj.stage_type = stage_type
                stage_obj.save()
        
        logger.info(f"Successfully loaded stage info to database")
    
    except Exception as e:
        logger.error(f"Failed to load stage info to database: {e}")


def clean_time(value):
    if pd.isna(value) or value in ['–', '-', '']:
        return None
    if isinstance(value, timedelta):
        return value
    # Add optional parsing here if it's a string like "4:42:39"
    return timedelta(seconds=value.total_seconds()) if hasattr(value, "total_seconds") else None


def load_stage_results(transformed_stage_results):
    try:
        for index, row in transformed_stage_results.iterrows():
            race = row['race']
            year = row['year']
            stage_number = row['stage_number']
            external_id = row['external_id']
            finishing_time = clean_time(row['finishing_time'])
            ranking = row['ranking']
            bonus = row['bonus']
            gc_rank = row.get('gc_rank')
            gc_time = row.get('gc_time')

            try:
                race_obj = Race.objects.get(url_reference=race, year=year)
            except Race.DoesNotExist:
                logger.warning(f"Race not found: {race} {year}. Skipping.")
                continue

            try:
                stage_obj = Stage.objects.get(race=race_obj, stage_number=stage_number)
            except Stage.DoesNotExist:
                logger.warning(f"Stage {stage_number} not found for {race} {year}. Skipping.")
                continue

            try:
                rider_obj = Rider.objects.get(external_id=external_id)
            except Rider.DoesNotExist:
                logger.warning(f"Rider {external_id} not found. Skipping.")
                continue


            # ✅ CONVERT EVERYTHING PROPERLY
            bonus = None if pd.isna(bonus) else timedelta(seconds=bonus.total_seconds())
            ranking = None if pd.isna(ranking) else ranking
            gc_rank = None if pd.isna(gc_rank) else gc_rank
            gc_time = None if pd.isna(gc_time) else timedelta(seconds=gc_time.total_seconds())

            # Save
            StageResult.objects.update_or_create(
                stage=stage_obj,
                rider=rider_obj,
                defaults={
                    'finishing_time': finishing_time,
                    'ranking': ranking,
                    'bonus': bonus,
                    'gc_rank': gc_rank,
                    'gc_time': gc_time
                }
            )

        
        logger.info(f"Successfully loaded stage results to database")
    
    except Exception as e:
        logger.error(f"Failed to load stage results to database: {e}")
