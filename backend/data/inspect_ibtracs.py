import pandas as pd


FILE = "data/raw/ibtracs.NI.list.v04r01.csv"


# IBTrACS has:
# Row 1 → column names
# Row 2 → units
# Row 3 onward → actual data
df = pd.read_csv(
    FILE,
    skiprows=[1],
    low_memory=False
)


print("\n========== IBTrACS LOADED SUCCESSFULLY ==========\n")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))


print("\n========== IMPORTANT COLUMNS ==========\n")

important_columns = [
    "SID",
    "SEASON",
    "NUMBER",
    "BASIN",
    "SUBBASIN",
    "NAME",
    "ISO_TIME",
    "NATURE",
    "LAT",
    "LON",
    "WMO_WIND",
    "WMO_PRES",
    "WMO_AGENCY"
]

print(df[important_columns].head(10).to_string(index=False))


print("\n========== COLUMN NAMES ==========\n")

print(df.columns.tolist())


print("\n========== DATA TYPES ==========\n")

print(df[important_columns].dtypes)


print("\n========== DONE ==========\n")