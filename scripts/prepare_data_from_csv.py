import os
from datetime import datetime
import re
import pandas as pd

# setting up current working directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

"""
# Function Tree
| prepare_en_dispensing_numbers()
| saveforkaggle_en_dispensing_numbers()
|____ prepare_en_dispensing_numbers()
"""

def prepare_en_dispensing_numbers():
    """Asks for user input to select a slice from en_dispensing_numbers table.

    Returns:
        df_en_dispensing_numbers (dataframe): Dispensing numbers between the range
        df_dispensers: Full dispensers table to merge later
    """

    # TODO Should add docstring

    # getting a dictionary of filenames and sorted keys
    list_of_files = os.listdir("../data/en_dispensing_numbers/")
    dict_of_files_with_month_and_date = {int(i[-7:-3]):f"20{i[-7:-5]}-{i[-5:-3]}-01" for i in list_of_files}
    sorted_list_of_keys = list(dict_of_files_with_month_and_date.keys())
    sorted_list_of_keys.sort()

    start_month = input(f"Please select a start date using 'YYMM' format. Select a value between {sorted_list_of_keys[0]} and {sorted_list_of_keys[-1]}")
    try:
        start_month = int(start_month)
    except:
        print("'start_month' is not a number. Please try again.")
        return start_month
    if start_month < sorted_list_of_keys[0] or start_month > sorted_list_of_keys[-1]:
        print("'start_month' is out of range. Please try again.")
        return start_month
    elif start_month not in sorted_list_of_keys:
        print("'start_month' is not in the months list. Please try again and select a start date using 'YYMM' format.")
        return start_month
    
    end_month = input(f"Please select a end date using 'YYMM' format. Select a value between {sorted_list_of_keys[0]} and {sorted_list_of_keys[-1]}")
    try:
        end_month = int(end_month)
    except:
        print("'end_month' is not a number. Please try again.")
        return end_month
    if end_month < sorted_list_of_keys[0] or end_month > sorted_list_of_keys[-1]:
        print("'end_month' is out of range. Please try again.")
        return end_month
    elif end_month not in sorted_list_of_keys:
        print("'end_month' is not in the months list. Please try again and select a end date using 'YYMM' format.")
        return end_month
    
    start_month_index = sorted_list_of_keys.index(start_month)
    end_month_index = sorted_list_of_keys.index(end_month)
    included_months = sorted_list_of_keys[start_month_index: end_month_index + 1]
    
    df_to_start = pd.read_csv(f"../data/en_dispensing_numbers/en_dispensing_numbers_{included_months[0]}.gz")
    df_to_start.insert(0, "Date", dict_of_files_with_month_and_date[included_months[0]])
    df_to_start["Date"] = pd.to_datetime( df_to_start["Date"])
    df_en_dispensing_numbers = df_to_start
    del df_to_start
    
    included_months.pop(0)
    
    for month in included_months:
        file_path = f"../data/en_dispensing_numbers/en_dispensing_numbers_{month}.gz"
        df = pd.read_csv(file_path)
        df.insert(0, "Date", dict_of_files_with_month_and_date[month])
        df["Date"] = pd.to_datetime( df["Date"])
        df_en_dispensing_numbers = pd.concat([df_en_dispensing_numbers, df])
    
    df_dispensers = pd.read_csv("../data/dispensers/dispensers.gz", compression="gzip")
    df_stps = pd.read_csv("../data/stps/stps.csv")
    
    return df_en_dispensing_numbers, df_dispensers, df_stps, start_month, end_month

def saveforkaggle_en_dispensing_numbers():

    # TODO Should add docstring

    df_en_dispensing_numbers, df_dispensers, df_stps, start_month, end_month = prepare_en_dispensing_numbers()

    now = datetime.now()
    date_string = now.strftime("%y%m%d-%H%M")
    folder_name = f"kaggle_export_{date_string}"
    os.mkdir(folder_name)

    df_en_dispensing_numbers.to_csv(f"{folder_name}/en_dispensing_numbers_{start_month}_{end_month}.csv", index=False, index_label=False)
    df_dispensers.to_csv(f"{folder_name}/dispensers.csv",  index=False, index_label=False)
    df_stps.to_csv(f"{folder_name}/stps.csv", index=False, index_label=False)
    print(f"en_dispensing_numbers_{start_month}_{end_month}.csv, dispensers.csv, and stps.csv are saved in {folder_name}")
