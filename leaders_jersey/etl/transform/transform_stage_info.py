import pandas as pd
from etl.logging_config import logger
from datetime import timedelta


def transform_stage_info(raw_stage_info):
    try:
        stage_info = pd.DataFrame(raw_stage_info)
        stage_info['stage_type'] = '-'
        logger.info(f"Successfully transformed stage info")
        return stage_info

    except Exception as e:
        logger.error(f"Failed to transform stage info: {e}") 


def safe_parse_timedelta(value, default="0:00:00"):
    """Parses a time string safely, correcting malformed formats like 0:00:-20 or 0:*0:39."""
    try:
        if not value or '*' in value or '-' in value and value.count('-') > 1:
            raise ValueError("Invalid or malformed time string")

        parts = value.strip().split(':')

        # Fix negative seconds like 0:00:-20 → -0:00:20
        if len(parts) == 3 and parts[2].startswith('-'):
            parts[2] = parts[2].lstrip('-')
            value = '-' + ':'.join(parts)

        return pd.to_timedelta(value)
    except Exception as e:
        logger.warning(f"Could not parse time value '{value}': {e}")
        return pd.to_timedelta(default)




def transform_stage_results(raw_stage_info, race, year, stage_number):
    try:
        stage_data = {}

        logger.info(f"Started stage results transformation")

        # Process stage results for each rider
        for rider in raw_stage_info.get('results', []):
            external_id = rider.get('rider_url', 'Unknown')
            if not external_id:
                continue

            stage_data[external_id] = {
                'external_id': external_id,
                'finishing_time': safe_parse_timedelta(rider.get('time')),
                'ranking': rider.get('rank', 'Unknown'),
                'bonus': safe_parse_timedelta(rider.get('bonus')),
            }

        # Add GC data
        for rider in raw_stage_info.get('gc', []):
            external_id = rider.get('rider_url')
            if not external_id:
                continue

            if external_id not in stage_data:
                stage_data[external_id] = {
                    'external_id': external_id,
                    'finishing_time': None,
                    'ranking': None,
                    'bonus': pd.to_timedelta('0:00:00'),
                }

            stage_data[external_id]['gc_time'] = safe_parse_timedelta(rider.get('time'))
            stage_data[external_id]['gc_rank'] = rider.get('rank')

        # Final structure
        stage_results = []
        for rider in stage_data.values():
            rider.update({
                'race': race,
                'year': year,
                'stage_number': stage_number
            })
            stage_results.append(rider)

        stage_results_df = pd.DataFrame(stage_results)

        # Convert ranking and gc_rank columns to nullable integers
        stage_results_df['ranking'] = stage_results_df['ranking'].where(stage_results_df['ranking'].notna(), None).astype('Int64')
        stage_results_df['gc_rank'] = stage_results_df['gc_rank'].where(stage_results_df['gc_rank'].notna(), None).astype('Int64')

        logger.info(f"Stage results transformed successfully")
        return stage_results_df

    except Exception as e:
        logger.error(f"Failed to transform stage results: {e}")
        return None