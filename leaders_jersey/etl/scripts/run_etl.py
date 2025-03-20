import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leaders_jersey.settings')
django.setup()

from ..extract.extract_startlist import extract_startlist
from ..transform.transform_startlist import transform_startlist
from ..load.load_startlist import load_startlist
from ..extract.extract_stage import extract_stage_info
from ..transform.transform_stage_info import transform_stage_info, transform_stage_results


# Run this script in the terminal: python -m etl.scripts.run_etl



race = "tour-de-france"
year = 2024

'''
raw_startlist = extract_startlist(race, year)
startlist_df = transform_startlist(raw_startlist)
load_startlist(startlist_df)
'''


raw_stage_data = extract_stage_info(race, year, 1)
stage_info = transform_stage_info(raw_stage_data, race, year, 1)
# stage_results = transform_stage_results(raw_stage_data, race, year, 1)

print(stage_info)
