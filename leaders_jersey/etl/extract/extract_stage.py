from procyclingstats import Stage

def extract_stage_info(race, year, stage_number):
    url = f"https://www.procyclingstats.com/race/{race}/{year}/stage-{stage_number}"
    stage_info_raw = Stage(url)
    return stage_info_raw.parse()
