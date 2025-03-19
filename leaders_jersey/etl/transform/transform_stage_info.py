import pandas as pd

def transform_stage_info(raw_stage_info, race, year, stage_number):
    stage_date = raw_stage_info.get('date', 'Unknown')
    stage_info = {'tour': f"{race} {year}",
                  'stage_number': stage_number,
                  'stage_date': stage_date,
                  'stage_type': None}
    
    return pd.DataFrame([stage_info])


def transform_stage_results(raw_stage_info, race, year, stage_number):
    stage_results = []
    for rider in raw_stage_info.get('gc', []):
        external_id = rider.get('rider_url', 'Unknown')
        finishing_time = pd.to_timedelta(rider.get('time', 'Unknown'))
        ranking = rider.get('rank', 'Unknown')
        bonus = round(pd.to_timedelta(rider.get('bonus', '0:00:00')).total_seconds())

        rider = {'stage_number': stage_number,
                 'race': race,
                 'year': year,
                 'external_id': external_id,
                 'finishing_time': finishing_time,
                 'ranking': ranking,
                 'bonus': bonus}
        
        stage_results.append(rider)
    
    stage_results_df = pd.DataFrame(stage_results)
    return stage_results_df
