import pandas as pd
from game.models import Stage

def load_stage_info(transformed_stage_info):
    for index, row in transformed_stage_info.iterrows():
        tour = row['tour']
        stage_number = row['stage_number']
        stage_date = row['stage_date']
        stage_type = row['stage_type']


