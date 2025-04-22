import pandas as pd
from etl.logging_config import logger


def transform_startlist(raw_startlist):
    try:
        logger.info(f"Started startlist transformation")
        transformed_startlist = []

        race = raw_startlist.get("race")
        year = raw_startlist.get("year")

        logger.debug(f"Transform input keys: {raw_startlist.keys()}")
        logger.debug(f"First rider sample: {raw_startlist.get('startlist')[0] if raw_startlist.get('startlist') else 'empty'}")

        if not isinstance(raw_startlist, dict):
            raise ValueError("transform_startlist expected a dictionary but got something else.")


        for rider in raw_startlist.get('startlist', []):
            rider_name = rider.get('rider_name', 'Unknown')
            team = rider.get('team_name', 'Unknown')
            nationality = rider.get('nationality', 'Unknown')
            external_id = rider.get('rider_url', 'Unknown')
            start_number = rider.get('rider_number', None)
        
            rider_info = {
                'rider_name': rider_name,
                'team': team,
                'nationality': nationality,
                'external_id': external_id,
                'start_number': start_number,
                'race': race,
                'year': year
            }
        
            transformed_startlist.append(rider_info)

        rider_df = pd.DataFrame(transformed_startlist)
        
        logger.info(f"Successfully transformed startlist with {len(rider_df)} riders")
        return rider_df
    
    except Exception as e:
        logger.error(f"Failed to transform the startlist: {e}")
        return None