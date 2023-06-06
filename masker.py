import json
import os
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderQuotaExceeded
from time import sleep

# Initialize the geocoder
geolocator = Nominatim(user_agent="geoapi_masker")

def get_city(lat, long):
    retries = 3
    for attempt in range(retries):
        
        try:
            location = geolocator.reverse([lat, long], exactly_one=True).raw
            return location.get('address', {}).get('city', 'Unknown')
        except GeocoderTimedOut:
            if attempt < retries - 1:  # if it's not the last attempt
                sleep(1)  # wait for 1 second before retrying
                continue
            else:  # this was the last attempt
                print(f"Geocoder service timed out after {retries} attempts")
                return 'Unknown'
        except GeocoderQuotaExceeded:
            print("Geocoder service quota exceeded")
            return 'Unknown'
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 'Unknown'

# Get list of files in the input directory
input_dir = 'input'
output_dir = 'output'
files = os.listdir(input_dir)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through the files
for file_name in files:
    #include progress bar
    print(f"Processing {file_name}, please wait...")

    # Open the file and load the JSON data
    with open(os.path.join(input_dir, file_name)) as f:
        data = json.load(f)

    # Extract the timelineObjects
    timelineObjects = data['timelineObjects']

    output_data = []

    # Loop through the timelineObjects
    for obj in timelineObjects:
        # Check if the object has an 'activitySegment'
        if 'activitySegment' in obj:
            segment = obj['activitySegment']

            # Extract start and end times
            start_time = segment['duration']['startTimestamp']
            end_time = segment['duration']['endTimestamp']

            # Convert timestamps to datetime objects
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            # Extract start and end locations
            start_location = segment['startLocation']
            end_location = segment['endLocation']

            # Convert the latitudes and longitudes to decimal format
            start_lat = start_location['latitudeE7'] / 1e7
            start_long = start_location['longitudeE7'] / 1e7
            end_lat = end_location['latitudeE7'] / 1e7
            end_long = end_location['longitudeE7'] / 1e7

            # Get city information from the coordinates
            start_city = get_city(start_lat, start_long)
            end_city = get_city(end_lat, end_long)

            # Add the data to the output
            output_data.append({
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'start_city': start_city,
                'end_city': end_city,
            })

    # log finished processing
    print(f"Finished processing {file_name}")

    # Write the output data to a new JSON file
    print(f"Writing converted to {output_dir} folder...")
    output_file_name = os.path.splitext(file_name)[0] + '_converted.json'
    with open(os.path.join(output_dir, output_file_name), 'w') as f:
        json.dump(output_data, f)
