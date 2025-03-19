import pandas as pd
from game.models import Rider

def load_startlist(transformed_startlist):
    Rider.objects.all().update(is_participating=False)

    for index, row in transformed_startlist.iterrows():
        rider_name = row['rider_name']
        team = row['team']
        nationality = row['nationality']
        external_id = row['external_id']
        start_number = row['start_number']

        rider_obj, created = Rider.objects.get_or_create(
            external_id=external_id,
            defaults={
                'rider_name': rider_name,
                'team': team,
                'nationality': nationality,
                'start_number': start_number,
                'is_participating': True
            }
        )

        if not created:
            rider_obj.rider_name = rider_name
            rider_obj.team = team
            rider_obj.nationality = nationality
            rider_obj.start_number = start_number
            rider_obj.is_participating = True
            rider_obj.save()


def delete_all_riders():
    Rider.objects.all().delete()