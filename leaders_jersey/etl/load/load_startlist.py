import pandas as pd
from game.models import Rider, Team
from etl.logging_config import logger


def load_startlist(transformed_startlist):
    try:
        Rider.objects.all().update(is_participating=False)

        for index, row in transformed_startlist.iterrows():
            rider_name = row['rider_name']
            team_name = row['team']
            nationality = row['nationality']
            external_id = row['external_id']
            start_number = row['start_number']

            if team_name:
                team_obj, _ =Team.objects.get_or_create(name=team_name)
            else:
                team_obj = None

            rider_obj, created = Rider.objects.get_or_create(
                external_id=external_id,
                defaults={
                    'rider_name': rider_name,
                    'team': team_obj,
                    'nationality': nationality,
                    'start_number': start_number,
                    'is_participating': True
                }
            )

            if not created:
                rider_obj.rider_name = rider_name
                rider_obj.team = team_obj
                rider_obj.nationality = nationality
                rider_obj.start_number = start_number
                rider_obj.is_participating = True
                rider_obj.save()
        
        logger.info(f"Successfully loaded startlist")
    
    except Exception as e:
        logger.error(f"Failed to load startlist: {e}")


def delete_all_riders():
    Rider.objects.all().delete()