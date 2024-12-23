import pandas as pd
import folium
from folium.plugins import MarkerCluster
from branca.colormap import LinearColormap

res_name = "Chili's restaurant"

def create_chilis_map(csv_file=f'{res_name}_coordinates_osm.csv'):
    """
    Create an interactive map showing Chili's restaurant locations
    
    Parameters:
    csv_file (str): Path to the CSV file containing location data
    """
    # Read the data
    df = pd.read_csv(csv_file)
    
    # Calculate the center point for the map
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Create a base map centered on the US
    m = folium.Map(location=[center_lat, center_lon], 
                  zoom_start=4,
                  tiles='cartodbpositron')
    
    # Add a marker cluster to handle many points efficiently
    marker_cluster = MarkerCluster().add_to(m)
    
    # Count locations per state for the color scaling
    state_counts = df['state'].value_counts()
    colormap = LinearColormap(colors=['yellow', 'red'],
                            vmin=state_counts.min(),
                            vmax=state_counts.max())
    
    # Add markers for each location
    for idx, row in df.iterrows():
        # Create popup content
        popup_content = f"""
            <div style="width:200px">
                <b>{row['name']}</b><br>
                {row['full_address']}<br>
                <small>Lat: {row['latitude']:.4f}, Lon: {row['longitude']:.4f}</small>
            </div>
        """
        
        # Add marker
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=folium.Popup(popup_content, max_width=300),
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            weight=2
        ).add_to(marker_cluster)
    
    # Add a title
    title_html = '''
        <div style="position: fixed; 
                    top: 10px; 
                    left: 50px; 
                    width: 300px; 
                    height: 90px; 
                    z-index:9999; 
                    background-color: white; 
                    padding: 10px; 
                    border-radius: 5px; 
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <h4>{} Restaurant Locations</h4>
            <p>Total Locations: {}</p>
            <p>States: {}</p>
        </div>
    '''.format(res_name, len(df), len(df['state'].unique()))
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Add state-level statistics
    state_stats = df.groupby('state').size().reset_index()
    state_stats.columns = ['State', 'Count']
    state_stats = state_stats.sort_values('Count', ascending=False)
    
    stats_html = '''
        <div style="position: fixed; 
                    bottom: 50px; 
                    right: 50px; 
                    width: 200px; 
                    max-height: 300px; 
                    overflow-y: auto; 
                    z-index:9999; 
                    background-color: white; 
                    padding: 10px; 
                    border-radius: 5px; 
                    box-shadow: 0 0 15px rgba(0,0,0,0.2);">
            <h4>Locations by State</h4>
            <table style="width:100%">
                <tr><th>State</th><th>Count</th></tr>
                {}
            </table>
        </div>
    '''.format(''.join(f'<tr><td>{row.State}</td><td>{row.Count}</td></tr>' for _, row in state_stats.iterrows()))
    m.get_root().html.add_child(folium.Element(stats_html))
    
    # Save the map
    output_file = f'{res_name}_locations_map.html'
    m.save(output_file)
    print(f"Map has been saved to {output_file}")
    
    return m

def main():
    """
    Main function to create the visualization
    """
    try:
        # Create the map
        create_chilis_map()
        print("Map created successfully!")
        
        # Print summary statistics
        df = pd.read_csv(f'{res_name}_coordinates_osm.csv')
        print(f"\nSummary Statistics:")
        print(f"Total locations found: {len(df)}")
        print(f"States covered: {len(df['state'].unique())}")
        print("\nTop 5 states by number of locations:")
        print(df['state'].value_counts().head())
        
    except FileNotFoundError:
        print("Error: Could not find the CSV file. Please run the data collection script first.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()