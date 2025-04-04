import pandas as pd
from game.models import Race, Stage, Rider, StageResult

def load_stage_info(transformed_stage_info):
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
            print(f"Race not found for {race} {year}. Skipping stage {stage_number}")
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


def load_stage_results(transformed_stage_results):
    for index, row in transformed_stage_results.iterrows():
        race = row['race']
        year = row['year']
        stage_number = row['stage_number']
        external_id = row['external_id']
        finishing_time = row['finishing_time']
        ranking = row['ranking']
        bonus = row['bonus']
        gc_rank = row.get('gc_rank')
        gc_time = row.get('gc_time')

        try:
            race_obj = Race.objects.get(url_reference=race, year=year)
        except Race.DoesNotExist:
            print(f"Race not found: {race} {year}. Skipping.")
            continue

        try:
            stage_obj = Stage.objects.get(race=race_obj, stage_number=stage_number)
        except Stage.DoesNotExist:
            print(f"Stage {stage_number} not found for {race} {year}. Skipping.")
            continue

        try:
            rider_obj = Rider.objects.get(external_id=external_id)
        except Rider.DoesNotExist:
            print(f"Rider {external_id} not found. Skipping.")
            continue

        ranking = None if pd.isna(ranking) else ranking
        gc_rank = None if pd.isna(gc_rank) else gc_rank
        gc_time = None if pd.isna(gc_time) else gc_time


        # Get or create the StageResult
        result_obj, created = StageResult.objects.get_or_create(
            stage=stage_obj,
            rider=rider_obj,
            defaults={
                'finishing_time': finishing_time,
                'ranking': ranking,
                'bonus': bonus
            }
        )

        if not created:
            result_obj.finishing_time = finishing_time
            result_obj.ranking = ranking
            result_obj.bonus = bonus
            result_obj.gc_rank = gc_rank
            result_obj.gc_time = gc_time
            result_obj.save()


