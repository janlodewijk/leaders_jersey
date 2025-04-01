from procyclingstats import Stage

def extract_stage_info(race, year):
    stages_info = []
    stage_number = 1
    max_stages = 30

    while stage_number <= max_stages:
        
        try:
            url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
            stage_info_raw = Stage(url)

            date = stage_info_raw.date()
            departure = stage_info_raw.departure()
            arrival = stage_info_raw.arrival()
            distance = stage_info_raw.distance()

        
            stage_info = {
                'race': race,
                'year': year,
                'stage_number': stage_number,
                'stage_date': date,
                'departure': departure,
                'arrival': arrival,
                'distance': round(distance)
            }

            stages_info.append(stage_info)
            stage_number += 1

        except Exception as e:
            print(f"Stopped extracting at stage {stage_number} Reason: {e}")
            break
    
    return stages_info
            
    


def extract_stage_results(race, year, stage_number):
    url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
    stage_results_raw = Stage(url)

    try:
        parsed_results = stage_results_raw.parse()
        return parsed_results
    
    except Exception as e:
        print(f"Stage {stage_number} not finished / no results yet. Error: {e}")
        return None