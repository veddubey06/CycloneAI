import pandas as pd

FILE = "data/raw/ibtracs.NI.list.v04r01.csv"

print("\n========== LOADING IBTRACS ==========\n")

df = pd.read_csv(
    FILE,
    skiprows=[1],
    low_memory=False
)

# Convert important columns
df["SEASON"] = pd.to_numeric(df["SEASON"], errors="coerce")
df["LAT"] = pd.to_numeric(df["LAT"], errors="coerce")
df["LON"] = pd.to_numeric(df["LON"], errors="coerce")
df["WMO_WIND"] = pd.to_numeric(df["WMO_WIND"], errors="coerce")
df["WMO_PRES"] = pd.to_numeric(df["WMO_PRES"], errors="coerce")

print("Total track records:", len(df))

print("\n========== STORM STATISTICS ==========\n")

print("Unique storms:", df["SID"].nunique())

print("Earliest year:", int(df["SEASON"].min()))
print("Latest year:", int(df["SEASON"].max()))

print("\n========== BASINS ==========\n")
print(df["SUBBASIN"].value_counts())

print("\n========== STORM NAMES ==========\n")
print(df["NAME"].value_counts().head(20))

print("\n========== WMO WIND ==========\n")
print(df["WMO_WIND"].describe())

print("\n========== WMO PRESSURE ==========\n")
print(df["WMO_PRES"].describe())

print("\n========== RECENT STORMS ==========\n")

recent = (
    df[
        (df["SEASON"] >= 2015)
        & (df["WMO_WIND"].notna())
    ][
        ["SID", "SEASON", "NAME", "SUBBASIN", "ISO_TIME",
         "LAT", "LON", "WMO_WIND", "WMO_PRES"]
    ]
    .head(20)
)

print(recent.to_string(index=False))

print("\n========== ANALYSIS COMPLETE ==========\n")