import pandas as pd
import zipfile

from package_name.config.data_path import GTFS_FILE

GTFS_PATH = GTFS_FILE
print("Using GTFS file:", GTFS_PATH)

with zipfile.ZipFile(GTFS_PATH) as z:
    print("Files in GTFS:")
    print(z.namelist())
    print("\n----------------------\n")

    # --- calendar.txt ---
    try:
        with z.open("calendar.txt") as f:
            calendar = pd.read_csv(f)
            print("calendar.txt:")
            print(calendar.head())
            print("\nDate range:")
            print("min start:", calendar["start_date"].min())
            print("max end:", calendar["end_date"].max())
    except KeyError:
        print("No calendar.txt found")

    print("\n----------------------\n")

    # --- calendar_dates.txt ---
    try:
        with z.open("calendar_dates.txt") as f:
            calendar_dates = pd.read_csv(f)
            print("calendar_dates.txt:")
            print(calendar_dates.head())
            print("\nUnique dates:")
            print(calendar_dates["date"].unique()[:10])
    except KeyError:
        print("No calendar_dates.txt found")

    print("\n----------------------\n")

    # --- trips.txt ---
    try:
        with z.open("trips.txt") as f:
            trips = pd.read_csv(f)
            print("trips.txt:")
            print("Number of trips:", len(trips))
            print("Unique service_ids:", trips["service_id"].nunique())
    except KeyError:
        print("No trips.txt found")