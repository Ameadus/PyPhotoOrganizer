import os
import subprocess
import argparse
from pathlib import Path
import mimetypes

# This needs to be done so mp4s are recognized as video files, os may not interpret mp4s as valid file extensions without this present
mimetypes.types_map['.mp4'] = 'video/mp4'


def get_date_taken(exiftool_path, file_path):
    """Get the date taken property from the file using ExifTool
    This relies on the format being YYYY:MM:DD:HH:SS other forms will not parse correctly.
    If your files are not in this format you may need to modify or convert your files metadata to the expected format
    """
    result = subprocess.run([exiftool_path, "-DateTimeOriginal", file_path], capture_output=True, text=True)
    date_taken = result.stdout.strip().split(": ")[-1]
    return date_taken


def move_file(photos_dir, exiftool_path, file_path, extensions):
    """Move the file to the correct directory based on its date taken property"""
    # Check if the file is any extension
    if not any(file_path.lower().endswith(extension) for extension in extensions):
        print(f"Skipping file: {file_path}")
        return

    print(f"Processing file: {file_path}")
    # Get the date taken property from the file
    date_taken = get_date_taken(exiftool_path, file_path)
    print(f"Date taken for {file_path}: {date_taken}")

    # Create directories for the year and month if they don't exist
    year_dir = os.path.join(photos_dir, date_taken[:4])
    month_dir = os.path.join(year_dir, date_taken[5:7])
    Path(year_dir).mkdir(parents=True, exist_ok=True)
    Path(month_dir).mkdir(parents=True, exist_ok=True)

    # Move the file to the month directory
    new_file_path = os.path.join(month_dir, os.path.basename(file_path))
    os.rename(file_path, new_file_path)


if __name__ == '__main__':
    print("Starting script...")
    parser = argparse.ArgumentParser(description="Sort photos by year using the ExifTool metadata.")
    parser.add_argument("photodir", metavar="PHOTO_DIRECTORY", help="The directory containing the photos to sort.")
    parser.add_argument("exiftool", metavar="EXIFTOOL_PATH", help="The path to the ExifTool executable.")
    args = parser.parse_args()

    # Accepted extensions for this tool
    extensions = ('.jpg', '.mp4', '.png', '.avi', '.mov', '.tif', '.gif')

    # Get the photo directory and ExifTool path from the command line arguments
    photos_dir = args.photodir
    exiftool_path = args.exiftool

    # Loop through each file in the directory tree and move it to the correct directory based on its date taken property
    for root, dirs, files in os.walk(photos_dir):
        for file in files:
            file_path = os.path.join(root, file)
            move_file(photos_dir, exiftool_path, file_path, extensions)

    # Wait for user input before exiting
    input("Press Enter to exit.")
