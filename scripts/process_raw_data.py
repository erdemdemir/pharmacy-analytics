import os
import re
import json
import pandas as pd

# setting up current working directory and raw_data folder
os.chdir(os.path.dirname(os.path.realpath(__file__)))


"""d
# Function Tree
| process_raw_data()
|____ process_en_dispensing_numbers()

"""

def process_raw_data():
    const_months = {"jan": 1, "feb": 2, "mar":3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
    raw_data_folder = "../data/_raw_data/"
    filtered_raw_files = [n for n in os.listdir(raw_data_folder) if n[-3:] in ["csv"]]
    not_processed = {} # Empty dict to keep track of problems

    for filename in filtered_raw_files:
        if len(re.findall("Dispensing", filename)) > 0:
            not_processed = process_en_dispensing_numbers(filename, const_months, raw_data_folder, not_processed)
        else:
            not_processed[filename] = "Problem with filename. Added by: process_raw_data()"
    
    if len(not_processed) > 0:
        print("The following files are not processed.", not_processed)

def process_en_dispensing_numbers(filename, const_months, raw_data_folder, not_processed):
    """Processes Pharmacy and appliance contractor dispensing data from 
    https://www.nhsbsa.nhs.uk/prescription-data/dispensing-data/dispensing-contractors-data

    Args:
        filename (string): Name of file to process, passed by process_raw_data()
        const_months (dictionary): Used to match filename and extract month number
        raw_data_folder (string): Relative path for raw data folder 
        not_processed (dictionary): Used to keep track of problems which causes unprocessed data files

    Returns:
        not_processed (dictionary): Used to keep track of problems which causes unprocessed data files

    Updates:
        [stps]: With new stps if applicable
        [dispensers]: With new dispensers if applicable
        [en_dispensing_numbers]: With new monthly data
        [processed_files_info.json]: With new monthly data
    """    
    # getting the newname for saving
    # TODO After adding several datasets, this block should be moved to process_raw_data()
    # TODO All filename exceptions should be handled before processing function call
    year = re.findall("\d+", filename)[0]
    month = [const_months[n] for n in const_months.keys() if n in filename.lower()][0]
    # ? Is there a better way to check this? It looks over complicated
    # ? What if there are 2 months name or more together in the filename? How to handle this?
    yearmonth = int(str(year) + str(month).zfill(2)) # e.g. 2005
    newname = f"en_dispensing_numbers_{yearmonth}"
    savepath = f"../data/en_dispensing_numbers/{newname}.gz"

    # loading raw data, cleaning colulmns, filtering pharmacies
    file_path = f"{raw_data_folder}{filename}"
    df_raw_csv = pd.read_csv(file_path)
    df_raw_csv.columns = [n.strip() for n in df_raw_csv.columns]
    df_raw_csv = df_raw_csv[df_raw_csv["Contractor Type"] == "Pharmacy"]

    # before processing, checking datatypes for problems
    df_numeric_columns = list(df_raw_csv.dtypes)[10:] # numeric columns
    if len([n for n in df_numeric_columns if str(n) != "int64" and str(n) != "float64"]) > 0:
        not_processed[filename] = "Problem with filename. Added by: process_en_dispensing_numbers()"
        return not_processed

    """
    TotalnumberofPrescriptions(ProfessionalFees) = TotalNofPrescProFees
    NumberofPrescriptions(ProfessionalFees)(Standarddiscountrate) = NofPrescProFeesStdDisc
    NumberofPrescriptions(ProfessionalFees)(Zerodiscountrate) = NofPrescProFeesZeroDisc
    """

    # extracting dispenser data
    df_dispensers = df_raw_csv.iloc[:, [0, 3 , 4, 5, 6, 7, 8, 9]]
    # TODO Should add column name check before selecting indexes
    df_dispensers = df_dispensers.fillna(value="")
    df_dispensers["DispenserAddress"] = df_dispensers["Address"] + " " + df_dispensers["Unnamed: 6"] + " " + df_dispensers["Unnamed: 7"] + " " + df_dispensers["Unnamed: 8"]
    df_dispensers = df_dispensers[["ContractorCode", "ContractorName", "DispenserAddress", "Postcode", "STPCode"]]
    df_dispensers.columns = ["DispenserCode", "DispenserName", "DispenserAddress", "DispenserPostcode", "STPCode"]
    df_dispensers["DispenserCode"] = df_dispensers["DispenserCode"].str.strip()
    df_dispensers["DispenserPostcode"] = df_dispensers["DispenserPostcode"].str.strip()
    df_dispensers["DispenserAddress"] = df_dispensers["DispenserAddress"].str.strip()
    df_dispensers["DispenserAddress"] = df_dispensers["DispenserAddress"].str.replace("   ", " ", regex=False).str.replace("  ", " ", regex=False)
    df_dispensers["STPCode"] = df_dispensers["STPCode"].str.strip()
    df_dispensers.insert(1, "DispenserType", "Pharmacy")
    
    # checking for new stps and updating if necessary
    stps = pd.read_csv("../data/stps/stps.csv")
    stps_from_df_raw_csv = df_raw_csv.drop_duplicates(subset="STPCode").iloc[:, [0, 1]]
    merged_stps = pd.merge(stps_from_df_raw_csv, stps, how="left", on="STPCode", suffixes=("_x", "_y"))
    new_stps = merged_stps[merged_stps["STP_y"].isnull()][["STPCode", "STP_x"]]
    if len(new_stps) > 0:
        new_stps.columns = ["STPCode", "STP"]
        combined_stps = pd.concat([stps, new_stps])
        combined_stps.to_csv("../data/stps/stps.csv", index=False, index_label=False)
    
    # TODO Maybe I can add Postcode check in the future for possible Pharmacy address changes

    # checking for new dispensers and updating if necessary
    dispensers = pd.read_csv("../data/dispensers/dispensers.gz", compression="gzip")
    merged_dispensers = pd.merge(df_dispensers, dispensers, how="left", on="DispenserCode", suffixes=("_x", "_y"))
    new_dispensers = merged_dispensers[merged_dispensers["DispenserName_y"].isnull()][["DispenserCode", "DispenserType_x", "DispenserName_x", "DispenserAddress_x", "DispenserPostcode_x", "STPCode_x"]]
    if len(new_dispensers) > 0:
        new_dispensers.columns = ["DispenserCode", "DispenserType", "DispenserName", "DispenserAddress", "DispenserPostcode", "STPCode"]
        combined_dispensers = pd.concat([dispensers, new_dispensers])
        combined_dispensers.to_csv("../data/dispensers/dispensers.gz", compression="gzip", index=False, index_label=False)
    
    # extracting and saving dispensing numbers
    dispensing_numbers = df_raw_csv.iloc[:, [3, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22]]
    dispensing_numbers.columns = ["DispenserCode", "NumberofForms", "NumberofItems", "TotalNofPrescProFees", "NofPrescProFeesStdDisc",  "NofPrescProFeesZeroDisc", "NumberofFormsEPS", "NumberofItemsEPS", "MUR", "NMS", "NumberofCOVID19HomeDeliveryFees"]
    dispensing_numbers.to_csv(savepath, compression="gzip", index=False, index_label=False)

    # updating processed_file_info
    # newname: {"columns":, "original_filename":}
    with open("processed_files_info.json", "r") as json_file:
        processed_files_info = json.load(json_file)
    processed_files_info[newname] = {"columns": list(df_raw_csv.columns), "original_filename": filename}
    with open("processed_files_info.json", "w") as json_file:
        json.dump(processed_files_info, json_file, indent = 4, sort_keys=True)
    
    # TODO Add move from _raw_data to _processed_data

    print(f"\"{filename}\" succesfully imported as \"{savepath}\". \
        \n\"dispensers/dispensers.gz\" is updated with {new_dispensers.shape[1]} new dispenser(s).")

    return not_processed