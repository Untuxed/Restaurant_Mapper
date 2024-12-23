import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from time import sleep
import time
from datetime import datetime, timedelta
import os

res_name = "Chili's restaurant"

def format_time(seconds):
    """
    Convert seconds into a human-readable format
    """
    return str(timedelta(seconds=round(seconds)))

def get_rest_coordinates(county_dir='/Users/liammartin/Downloads/us_counties/dist/'):
    """
    Fetch latitude and longitude coordinates for res_name restaurants in the US
    using OpenStreetMap's Nominatim service, with timing information.
    
    Returns:
    tuple: (locations list, timing dictionary)
    """
    # Initialize the geolocator
    geolocator = Nominatim(user_agent=f"{res_name}_restaurant_finder")
    
    # List to store restaurant location data
    locations = []
    
    # Timing statistics
    timing_stats = {
        'start_time': datetime.now(),
        'end_time': None,
        'total_duration': None,
        'states_processed': 0,
        'locations_found': 0,
        'state_timings': {},
        'timeouts': 0,
        'errors': 0
    }
    
    # List of US states
    us_states = [
        "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "IA", "ID", "IL", 
        "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", 
        "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA",
        "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WI"
    ]
    
    total_states = len(us_states)
    
    for index, state in enumerate(us_states, 1):
        state_start_time = time.time()
        state_results = 0  # Track results for the state
        
        print(f"\nProcessing {state} ({index}/{total_states})...")
        
        # Load county list for the state
        county_list = pd.read_json(os.path.join(county_dir, f"{state}.json"))

        # Loop through each county in the state
        for i, data in county_list.iterrows():
            county = data["County"]
            state = data["State"]
            
            county_start_time = time.time()
            county_results = 0  # Track results for the county
            
            # Create the geocoding query for the specific county and state
            query = f"{res_name}, {county}, {state}, United States"

            # Perform geocoding query for the county
            results = geolocator.geocode(
                query,
                exactly_one=False,
                limit=50,
                country_codes="us"
            )

            if results:
                for location in results:
                    loc_name = location.address.split(",")[0]  # Extract the name from the address
                    if location:  # Filter out empty or invalid locations
                        locations.append({
                            'name': loc_name,
                            'full_address': location.address,
                            'latitude': location.latitude,
                            'longitude': location.longitude,
                            'state': state,
                            'county': county
                        })
                        county_results += 1
            
            # Update county duration and results
            county_duration = time.time() - county_start_time
            timing_stats['locations_found'] += county_results
            state_results += county_results
        
        # Calculate state timing and results
        state_duration = time.time() - state_start_time
        timing_stats['state_timings'][state] = {
            'duration': state_duration,
            'locations_found': county_results
        }
        timing_stats['locations_found'] += county_results
        timing_stats['states_processed'] += 1
        
        # State progress update
        elapsed_time = time.time() - timing_stats['start_time'].timestamp()
        print(f"Found {state_results} locations in {state} ({format_time(state_duration)})")
        print(f"Progress: {index}/{total_states} states processed")

        sleep(1)  # Rate limiting
    
    # Final timing stats
    timing_stats['end_time'] = datetime.now()
    timing_stats['total_duration'] = (timing_stats['end_time'] - timing_stats['start_time']).total_seconds()
    
    return locations, timing_stats

def generate_timing_report(timing_stats):
    """
    Generate a detailed timing report
    """
    report = []
    report.append("\n=== TIMING REPORT ===")
    report.append(f"Start Time: {timing_stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"End Time: {timing_stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Duration: {format_time(timing_stats['total_duration'])}")
    report.append(f"Total States Processed: {timing_stats['states_processed']}/50")
    report.append(f"Total Locations Found: {timing_stats['locations_found']}")
    report.append(f"Average Locations per State: {timing_stats['locations_found']/max(1, timing_stats['states_processed']):.1f}")
    report.append(f"Timeouts Encountered: {timing_stats['timeouts']}")
    report.append(f"Errors Encountered: {timing_stats['errors']}")
    
    # State-by-state breakdown
    report.append("\nTop 5 States by Number of Locations:")
    sorted_states = sorted(
        timing_stats['state_timings'].items(),
        key=lambda x: x[1]['locations_found'],
        reverse=True
    )[:5]
    
    for state, stats in sorted_states:
        report.append(f"{state}: {stats['locations_found']} locations in {format_time(stats['duration'])}")
    
    return "\n".join(report)

def main():
    print("Starting search for {res_name} restaurants...")
    start_time = time.time()
    
    # Get coordinates and timing information
    locations, timing_stats = get_rest_coordinates()
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(locations)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{res_name}_coordinates_osm.csv'
    df.to_csv(filename, index=False)
    
    # Generate and print timing report
    print(generate_timing_report(timing_stats))
    
    # Save timing report
    report_filename = f'{res_name}_timing_report.txt'
    with open(report_filename, 'w') as f:
        f.write(generate_timing_report(timing_stats))
    
    print(f"\nResults saved to {filename}")
    print(f"Timing report saved to {report_filename}")

if __name__ == "__main__":
    main()