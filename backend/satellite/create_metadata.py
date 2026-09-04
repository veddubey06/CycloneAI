import json
import os


# ==========================================
# NISARGA SAMPLE
# ==========================================

SAMPLE = {
    "storm_id": "2020153N13072",
    "storm_name": "NISARGA",

    "basin": "North Indian Ocean",
    "sub_basin": "Arabian Sea",

    "timestamp": "2020-06-03 12:00:00",

    "latitude": 19.1,
    "longitude": 73.7,

    "wind_speed_kt": 55,
    "pressure_hpa": 984,

    "satellite": "Himawari-8",
    "sensor": "AHI",
    "band": "B13",

    "image_type": "infrared",
    "image_size": "512x512",

    "image_file": "nisarga_b13_geographic_512.png",

    "source": "NOAA Himawari-8 + IBTrACS"
}


# ==========================================
# OUTPUT FOLDER
# ==========================================

timestamp = SAMPLE["timestamp"]

folder_timestamp = timestamp.replace(
    "-", ""
).replace(
    ":", ""
).replace(
    " ", "_"
)

# Convert:
# 2020-06-03 09:00:00
# →
# 20200603_090000

# We only want:
# 20200603_0900

folder_timestamp = folder_timestamp[:13]

output_folder = os.path.join(
    "data",
    "processed",
    "satellite",
    f"nisarga_{folder_timestamp}"
)

os.makedirs(
    output_folder,
    exist_ok=True
)


# ==========================================
# SAVE METADATA
# ==========================================

output_file = os.path.join(
    output_folder,
    "metadata.json"
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        SAMPLE,
        file,
        indent=4
    )


# ==========================================
# DISPLAY
# ==========================================

print("\n==========================================")
print("       METADATA CREATED")
print("==========================================\n")

print("Storm      :", SAMPLE["storm_name"])
print("Timestamp  :", SAMPLE["timestamp"])
print("Latitude   :", SAMPLE["latitude"])
print("Longitude  :", SAMPLE["longitude"])
print("Wind       :", SAMPLE["wind_speed_kt"], "kt")
print("Pressure   :", SAMPLE["pressure_hpa"], "hPa")
print("Satellite  :", SAMPLE["satellite"])
print("Band       :", SAMPLE["band"])

print("\nMetadata file:")
print(output_file)

print("\n==========================================")