from datetime import datetime
import subprocess


BUCKET = "s3://noaa-himawari8/AHI-L1b-FLDK"


def get_himawari_path(timestamp):
    """Convert IBTrACS timestamp to Himawari AWS folder."""

    dt = datetime.strptime(
        timestamp,
        "%Y-%m-%d %H:%M:%S"
    )

    return (
        f"{BUCKET}/"
        f"{dt:%Y/%m/%d/%H%M}/"
    )


def check_b13_available(timestamp):
    """Check whether Himawari B13 files exist."""

    path = get_himawari_path(timestamp)

    command = [
        "aws",
        "s3",
        "ls",
        "--no-sign-request",
        path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    b13_files = [
        line
        for line in result.stdout.splitlines()
        if "B13" in line
    ]

    return path, b13_files


if __name__ == "__main__":

    test_times = [
        "2020-06-03 06:00:00",
        "2020-06-03 09:00:00",
        "2020-06-03 12:00:00"
    ]

    print("\n==========================================")
    print("     HIMAWARI AWS AVAILABILITY CHECK")
    print("==========================================\n")

    for timestamp in test_times:

        print("IBTrACS timestamp:")
        print(timestamp)

        path, files = check_b13_available(timestamp)

        print("\nAWS path:")
        print(path)

        print("B13 segments found:", len(files))

        if files:
            print("Status: AVAILABLE ✅")
        else:
            print("Status: NOT AVAILABLE ❌")

        print("------------------------------------------")

    print("\nAVAILABILITY CHECK COMPLETED")