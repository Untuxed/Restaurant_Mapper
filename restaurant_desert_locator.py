import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.point import Point
import folium
from tqdm import tqdm
import contextily as ctx
import geopandas as gpd
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt
import os

res_name = "chili"

def load_and_prep_data(csv_file=f"{res_name}_coordinates_osm.csv"):
    """Load locations and return as list of coordinates"""
    df = pd.read_csv(csv_file)
    return list(zip(df['latitude'], df['longitude']))

def get_us_boundary():
    """Get continental US boundary using geopandas"""
    usa = gpd.read_file(os.path.join(os.path.dirname(__file__), "map_data/ne_110m_admin_0_countries.shp"))
    # Filter for continental US (excluding Alaska and Hawaii)
    cont_usa = usa[usa['NAME'] == 'United States of America'].explode()
    cont_usa = cont_usa[~cont_usa.geometry.apply(lambda x: x.centroid.y > 50)]  # Exclude Alaska
    cont_usa = cont_usa[~cont_usa.geometry.apply(lambda x: x.centroid.y < 25)]  # Exclude Hawaii
    return cont_usa

def create_search_grid(boundary, resolution=0.5):
    """Create a grid of points within the continental US"""
    # Get bounds of continental US
    minx, miny, maxx, maxy = boundary.total_bounds
    
    # Create grid points
    x = np.arange(minx, maxx, resolution)
    y = np.arange(miny, maxy, resolution)
    xx, yy = np.meshgrid(x, y)
    
    # Convert to list of points
    points = []
    for i in range(len(xx.flat)):
        point = ShapelyPoint(xx.flat[i], yy.flat[i])
        # Only include points within continental US
        if boundary.geometry.contains(point).any():
            points.append((yy.flat[i], xx.flat[i]))  # Note: y is lat, x is lon
    
    return points

def find_furthest_point(res_locations, search_points, progress_bar=True):
    """Find the point furthest from any Chili's location"""
    max_distance = 0
    furthest_point = None
    
    iterator = tqdm(search_points) if progress_bar else search_points
    
    for point in iterator:
        # Find minimum distance to any Chili's
        min_distance = min(geodesic(point, res).miles for res in res_locations)
        
        if min_distance > max_distance:
            max_distance = min_distance
            furthest_point = point
    
    return furthest_point, max_distance

def create_visualization(res_locations, furthest_point, max_distance):
    """Create an interactive map showing the results"""
    # Create base map centered on furthest point
    m = folium.Map(location=furthest_point, zoom_start=6)
    
    # Add Chili's locations
    for loc in res_locations:
        folium.CircleMarker(
            location=loc,
            radius=3,
            color='red',
            fill=True,
            popup=f'{res_name} Location'
        ).add_to(m)
    
    # Add furthest point
    folium.CircleMarker(
        location=furthest_point,
        radius=8,
        color='blue',
        fill=True,
        popup=f'Furthest Point<br>Distance to nearest {res_name}: {max_distance:.1f} miles'
    ).add_to(m)
    
    # Add distance circle
    folium.Circle(
        location=furthest_point,
        radius=max_distance * 1609.34,  # Convert miles to meters
        color='blue',
        fill=False,
        popup=f'Distance to nearest {res_name}'
    ).add_to(m)
    
    return m

def main():
    print("Loading data...")
    res_locations = load_and_prep_data()
    
    print("Loading US boundary...")
    boundary = get_us_boundary()
    
    print("Creating search grid...")
    search_points = create_search_grid(boundary, resolution=0.5)
    
    print("Finding furthest point...")
    furthest_point, max_distance = find_furthest_point(res_locations, search_points)
    
    print(f"\nResults:")
    print(f"Furthest point from any {res_name}:")
    print(f"Latitude: {furthest_point[0]:.4f}")
    print(f"Longitude: {furthest_point[1]:.4f}")
    print(f"Distance to nearest {res_name}: {max_distance:.1f} miles")
    
    print("\nCreating visualization...")
    m = create_visualization(res_locations, furthest_point, max_distance)
    m.save(f'{res_name}_furthest_point.html')
    print(f"Map saved as '{res_name}_furthest_point.html'")

if __name__ == "__main__":
    main()