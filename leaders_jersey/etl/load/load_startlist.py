from game.models import Rider, Team, Race, StartlistEntry
from etl.logging_config import logger
import pandas as pd


def load_startlist(transformed_startlist):
    try:
        created_count = 0
        updated_count = 0

        # Group by race
        races = transformed_startlist.groupby(['race', 'year'])

        for (race_slug, year), group in races:
            # Get race object
            try:
                race_obj = Race.objects.get(url_reference=race_slug, year=year)
            except Race.DoesNotExist:
                logger.warning(f"Race not found: {race_slug} ({year}) — skipping group")
                continue

            # 🧹 Clean up old entries
            incoming_external_ids = group['external_id'].tolist()
            existing_entries = StartlistEntry.objects.filter(race=race_obj)
            entries_to_delete = existing_entries.exclude(rider__external_id__in=incoming_external_ids)
            deleted_count, _ = entries_to_delete.delete()
            if deleted_count:
                logger.info(f"Removed {deleted_count} obsolete startlist entries for {race_obj}")

            for index, row in group.iterrows():
                rider_name = row['rider_name']
                team_name = row['team']
                short_team_name = row.get('short_team') or team_name
                nationality = row['nationality']
                external_id = row['external_id']
                start_number = int(row['start_number']) if pd.notna(row['start_number']) else None

                # Get or create team
                team_obj, _ = Team.objects.get_or_create(
                    name=team_name,
                    defaults={'short_name': short_team_name}
                )

                # Update short_name if changed
                if team_obj.short_name != short_team_name:
                    team_obj.short_name = short_team_name
                    team_obj.save()

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

                # Update rider fields
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
