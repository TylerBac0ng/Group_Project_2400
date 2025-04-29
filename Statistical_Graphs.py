import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
import geopandas as gpd
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import Point


# Load dataset (only necessary columns)
df = pd.read_csv('Crimes_-_2001_to_Present.csv', usecols=[
    'Date', 'Primary Type', 'Description', 'Arrest', 'District', 'Community Area','Latitude', 'Longitude'
], low_memory=False)

# Parse Date and drop invalid ones
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])

# Convert text to lowercase
df['Description'] = df['Description'].astype(str).str.lower()
df['Primary Type'] = df['Primary Type'].astype(str).str.lower()

# Filter gun-related crimes
gun_keywords = ['gun', 'firearm', 'rifle', 'pistol', 'handgun', 'shotgun', 'revolver', 'shooting', 'weapon']
gun_crimes = df[df['Description'].str.contains('|'.join(gun_keywords), na=False)].copy()
gun_crimes = gun_crimes[~gun_crimes['Description'].str.contains('knife|blunt|taser|weapon - other', na=False)]

# Add Year column
gun_crimes['Year'] = gun_crimes['Date'].dt.year
gun_crimes['Hour'] = gun_crimes['Date'].dt.hour
gun_crimes['Month'] = gun_crimes['Date'].dt.month
gun_crimes['DayOfWeek'] = gun_crimes['Date'].dt.dayofweek

# --- Reduce the data to manageable size ---
# Optional: if gun_crimes still has >100k rows, sample down
if len(gun_crimes) > 50000:
    gun_crimes = gun_crimes.sample(50000, random_state=1)

# Filter out invalid coordinates
gun_crimes_geo = gun_crimes.dropna(subset=['Latitude', 'Longitude']).copy()
gun_crimes_geo = gun_crimes_geo[(gun_crimes_geo['Latitude'] > 41.6) & 
                                (gun_crimes_geo['Latitude'] < 42.1) & 
                                (gun_crimes_geo['Longitude'] > -88.0) & 
                                (gun_crimes_geo['Longitude'] < -87.5)]

# Create geometry column from lat/long
geometry = [Point(xy) for xy in zip(gun_crimes_geo['Longitude'], gun_crimes_geo['Latitude'])]
gdf = gpd.GeoDataFrame(gun_crimes_geo, geometry=geometry)
gdf.crs = "EPSG:4326"
gdf_webmerc = gdf.to_crs(epsg=3857)

# --- Plots ---

# 1. Histogram: Number of Gun Crimes per Year
plt.figure(figsize=(10,5))
gun_crimes['Year'].value_counts().sort_index().plot(kind='bar')
plt.title('Gun Crimes per Year')
plt.xlabel('Year')
plt.ylabel('Number of Incidents')
plt.tight_layout()
plt.show()

# 2. Bar Plot: Arrest Rate by Primary Type
plt.figure(figsize=(12,6))
top_primary_types = gun_crimes['Primary Type'].value_counts().nlargest(10).index
arrest_rate = gun_crimes[gun_crimes['Primary Type'].isin(top_primary_types)].groupby('Primary Type')['Arrest'].mean().sort_values(ascending=False) * 100
arrest_rate.plot(kind='bar')
plt.title('Arrest Rate for Top Gun Crime Types')
plt.ylabel('Arrest Rate (%)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 3. Violin Plot: Top 10 Community Areas
top_areas = gun_crimes['Community Area'].value_counts().nlargest(10).index
plt.figure(figsize=(14,6))
sns.violinplot(x='Community Area', y='Year', data=gun_crimes[gun_crimes['Community Area'].isin(top_areas)], inner='quartile')
plt.title('Gun Crime Distribution in Top Community Areas')
plt.xlabel('Community Area')
plt.ylabel('Year')
plt.tight_layout()
plt.show()

# 4. Trendline: Year vs Number of Gun Crimes
crime_trend = gun_crimes.groupby('Year').size().reset_index(name='Crime Count')
plt.figure(figsize=(10,5))
sns.regplot(x='Year', y='Crime Count', data=crime_trend, scatter=True, ci=None, line_kws={"color": "blue"})
plt.title('Gun Crime Trend Over Years')
plt.xlabel('Year')
plt.ylabel('Number of Gun Crimes')
plt.tight_layout()
plt.show()

# 5. Time of Day Analysis (Hourly Distribution)
plt.figure(figsize=(12,5))
gun_crimes['Hour'].value_counts().sort_index().plot(kind='bar', color='navy')
plt.title('Gun Crimes by Hour of Day')
plt.xlabel('Hour (24-hour format)')
plt.ylabel('Number of Gun Crimes')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('gun_crimes_by_hour.png', dpi=300)
plt.show()
plt.close()

# 6. District Map - Bubble Plot
# Aggregate gun crimes by district
district_counts = gdf.groupby('District').size().reset_index(name='count')

# Calculate centroids of points in each district
district_centroids = {}
for district in gdf['District'].unique():
    district_data = gdf[gdf['District'] == district]
    if len(district_data) > 0:
        mean_lon = district_data['Longitude'].mean()
        mean_lat = district_data['Latitude'].mean()
        district_centroids[district] = Point(mean_lon, mean_lat)

# Create a district GeoDataFrame with centroids
district_gdf = gpd.GeoDataFrame(
    district_counts, 
    geometry=[district_centroids.get(d, Point(0, 0)) for d in district_counts['District']]
)
district_gdf.crs = "EPSG:4326"
district_gdf = district_gdf.to_crs(epsg=3857)

# Plot districts by count
fig, ax = plt.subplots(figsize=(14, 12))

# Plot district points sized by crime count
district_gdf.plot(
    ax=ax,
    column='count',
    cmap='Blues',
    legend=True,
    markersize=district_gdf['count'] / district_gdf['count'].max() * 500,  # Scale marker sizes
    alpha=0.7,
    legend_kwds={'label': "Gun Crimes per District"}
)

# Add district labels
for idx, row in district_gdf.iterrows():
    plt.annotate(
        f"District {row['District']}\n({row['count']} crimes)",
        xy=(row.geometry.x, row.geometry.y),
        xytext=(0, 0),
        textcoords="offset points",
        ha='center',
        fontsize=9,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
    )

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=11)

plt.title('Gun Crimes by Chicago Police District', fontsize=16)
ax.set_axis_off()
plt.tight_layout()
plt.savefig('district_bubble_map.png', dpi=300, bbox_inches='tight')
plt.show()
plt.close()

# 7. Monthly Pattern Analysis
plt.figure(figsize=(12,5))
gun_crimes['Month'].value_counts().sort_index().plot(kind='line', marker='o', linewidth=2, markersize=8, color='darkblue')
plt.title('Gun Crimes by Month')
plt.xlabel('Month')
plt.ylabel('Number of Gun Crimes')
plt.xticks(range(1,13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.grid(linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('gun_crimes_by_month.png', dpi=300)
plt.show()
plt.close()
