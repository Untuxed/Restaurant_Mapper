# Restaurant Mapper and Desert Locator

A suite of Python scripts for collecting, analyzing, and visualizing restaurant location data across the United States.

## Scripts

### restaurant_locator.py
Collects restaurant location data using OpenStreetMap's Nominatim service:
- Searches by county and state
- Generates CSV with coordinates and location details
- Handles rate limiting and error tracking

### restaurant_visualizer.py
Creates interactive web visualizations of restaurant locations:
- Generates clustered marker map
- Shows state-by-state statistics
- Outputs HTML file with complete visualization

### restaurant_desert_locator.py
Finds the point furthest from any restaurant location:
- Uses geodesic distance calculations
- Creates search grid across continental US
- Generates interactive map showing furthest point
- Visualizes distance radius to nearest location

## Requirements

```
pandas
numpy
geopy
folium
tqdm
contextily
geopandas
shapely
matplotlib
```

## Usage

1. Set restaurant name in each script:
```python
res_name = "Restaurant Name"
```

2. Run data collection:
```bash
python restaurant_locator.py
```

3. Create visualization:
```bash
python restaurant_visualizer.py
```

4. Find restaurant deserts:
```bash
python restaurant_desert_locator.py
```

## Output Files

- `{restaurant}_coordinates_osm.csv`: Location data
- `{restaurant}_timing_report.txt`: Collection statistics
- `{restaurant}_locations_map.html`: Interactive visualization
- `{restaurant}_furthest_point.html`: Desert analysis map

## Notes

- Requires US county data in `./county_data/`
- Requires Open Street Map .osm file in `./map_data/`
- Uses OpenStreetMap data via Nominatim API
- Respects API rate limits
- Files are saved in working directory
