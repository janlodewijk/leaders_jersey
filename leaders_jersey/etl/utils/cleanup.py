from game.models import StageResult, Stage, Race
import logging

logger = logging.getLogger(__name__)

def delete_stage_results(race_slug, year, stage_number):
    try:
        from django.db import transaction

        race = Race.objects.get(url_reference=race_slug, year=year)
        stage = Stage.objects.get(race=race, stage_number=stage_number)

        with transaction.atomic():
            deleted, _ = StageResult.objects.filter(stage=stage).delete()
            logger.info(f"✅ Deleted {deleted} results for stage {stage_number} of {race_slug} ({year})")

    except Exception as e:
        logger.error(f"❌ Failed to delete results for stage {stage_number}: {e}")