from game.models import Rider, Team, Race, StartlistEntry
from etl.logging_config import logger


def load_startlist(transformed_startlist):
    try:
        created_count = 0
        updated_count = 0

        for index, row in transformed_startlist.iterrows():
            rider_name = row['rider_name']
            team_name = row['team']
            nationality = row['nationality']
            external_id = row['external_id']
            start_number = row['start_number']
            race_slug = row['race']
            year = row['year']

            # Get race object
            try:
                race_obj = Race.objects.get(url_reference=race_slug, year=year)
            except Race.DoesNotExist:
                logger.warning(f"Race not found: {race_slug} ({year}) — skipping rider {rider_name}")
                continue

            # Get or create team
            team_obj = None
            if team_name:
                team_obj, _ = Team.objects.get_or_create(name=team_name)

            # Get or create rider
            rider_obj, _ = Rider.objects.get_or_create(
                external_id=external_id,
                defaults={
                    'rider_name': rider_name,
                    'team': team_obj,
                    'nationality': nationality,
                    'start_number': start_number,
                }
            )

            # Update rider if needed
            rider_obj.rider_name = rider_name
            rider_obj.nationality = nationality
            rider_obj.team = team_obj
            rider_obj.start_number = start_number
            rider_obj.save()

            # Create or update StartlistEntry
            entry, created = StartlistEntry.objects.get_or_create(
                race=race_obj,
                rider=rider_obj,
                defaults={
                    'team': team_obj,
                    'start_number': start_number
                }
            )

            if not created:
                entry.team = team_obj
                entry.start_number = start_number
                entry.save()
                updated_count += 1
            else:
                created_count += 1

        logger.info(f"Loaded startlist: {created_count} new, {updated_count} updated")

    except Exception as e:
        logger.error(f"Failed to load startlist: {e}")