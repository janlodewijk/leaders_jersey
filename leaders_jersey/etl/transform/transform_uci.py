import pandas as pd
import os
# from etl.logging_config import logger

def transform_uci_points(race_slug):
    try:
        uci_df = pd.read_excel(f"etl/data/uci_points/{race_slug}.xlsx")

        if 'gc_rank' not in uci_df.columns or 'uci_points' not in uci_df.columns:
            print("Missing required columns: gc_rank and/or uci_points")
            return
        
        if not uci_df['gc_rank'].is_unique:
            print("Duplicate GC ranks found in file")
            return
        
        if not pd.to_numeric(uci_df['uci_points'], errors='coerce').notna().all():
            print("Some UCI points are not valid numbers")
            return
        
        uci_dict = uci_df.set_index('gc_rank')['uci_points'].to_dict()
        return(uci_dict)

    except Exception as e:
        print(f"Failed to transform file from {race_slug}: {e}")