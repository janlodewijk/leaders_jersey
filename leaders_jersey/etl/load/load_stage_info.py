import pandas as pd
from game.models import Race, Stage

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


