import pandas as pd

def transform_stage_info(raw_stage_info):
    stage_info = pd.DataFrame(raw_stage_info)
    stage_info['stage_type'] = '-'

    return stage_info


def transform_stage_results(raw_stage_info, race, year, stage_number):
    stage_data = {}

    # Process stage results
    for rider in raw_stage_info.get('results', []):
        external_id = rider.get('rider_url', 'Unknown')
        if not external_id:
            continue
        stage_data[external_id] = {
            'external_id': external_id,
            'finishing_time': pd.to_timedelta(rider.get('time', '0:00:00')),
            'ranking': rider.get('rank', 'Unknown'),
            'bonus': pd.to_timedelta(rider.get('bonus', '0:00:00')),
        }
    
    # Add GC data
    for rider in raw_stage_info.get('gc', []):
        external_id = rider.get('rider_url')
        if not external_id:
            continue
        if external_id not in stage_data:
            stage_data[external_id] ={
                'external_id': external_id,
                'finishing_time': None,
                'ranking': None,
                'bonus': pd.to_timedelta('0:00:00'),
            }
        
        stage_data[external_id]['gc_time'] = pd.to_timedelta(rider.get('time', '0:00:00'))
        stage_data[external_id]['gc_rank'] = rider.get('rank')

    stage_results = []
    for rider in stage_data.values():
        rider.update({
            'race': race,
            'year': year,
            'stage_number': stage_number
        })
        stage_results.append(rider)
    
    stage_results_df = pd.DataFrame(stage_results)
    stage_results_df = pd.DataFrame(stage_results)

    # Convert ranking and gc_rank columns to nullable integers
    stage_results_df['ranking'] = stage_results_df['ranking'].astype("Int64")
    stage_results_df['gc_rank'] = stage_results_df['gc_rank'].astype("Int64")

    stage_results_df = stage_results_df.where(pd.notnull(stage_results_df), None)



    return stage_results_df

