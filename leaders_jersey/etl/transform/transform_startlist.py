import pandas as pd

def transform_startlist(raw_startlist):
    transformed_startlist = []
    for rider in raw_startlist.get('startlist', []):
        rider_name = rider.get('rider_name', 'Unknown')
        team = rider.get('team_name', 'Unknown')
        nationality = rider.get('nationality', 'Unknown')
        external_id = rider.get('rider_url', 'Unknown')
        start_number = rider.get('rider_number', 'Unknown')
    
        rider_info = {'rider_name': rider_name,
                    'team': team,
                    'nationality': nationality,
                    'external_id': external_id,
                    'start_number': start_number}
    
        transformed_startlist.append(rider_info)

    rider_df = pd.DataFrame(transformed_startlist)
    
    return rider_df
    