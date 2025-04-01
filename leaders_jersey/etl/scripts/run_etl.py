import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'leaders_jersey.settings')
django.setup()

from ..extract.extract_startlist import extract_startlist
from ..transform.transform_startlist import transform_startlist
from ..load.load_startlist import load_startlist
from ..extract.extract_stage import extract_stage_info, extract_stage_results
from ..transform.transform_stage_info import transform_stage_info, transform_stage_results
from ..load.load_stage_info import load_stage_info, load_stage_results


# Run this script in the terminal: python -m etl.scripts.run_etl



race = "international-tour-of-hellas"
year = 2025


raw_startlist = extract_startlist(race, year)
startlist_df = transform_startlist(raw_startlist)
load_startlist(startlist_df)



'''
raw_stage_data = extract_stage_info(race, year)
stage_info = transform_stage_info(raw_stage_data, race, year)
print(stage_info.head())
load_stage_info(stage_info)
'''

'''
raw_results = extract_stage_results(race, year, stage)
trans_results = transform_stage_results(raw_results, race, year, stage)
load_stage_results(trans_results)
'''