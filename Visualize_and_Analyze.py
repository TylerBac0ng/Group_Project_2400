import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your dataset
df = pd.read_csv('Crimes_-_2001_to_Present.csv', low_memory=False)

# Preprocessing
df['Description'] = df['Description'].astype(str).str.lower()
df['Primary Type'] = df['Primary Type'].astype(str).str.lower()
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

# Filter gun-related crimes
gun_keywords = ['gun', 'firearm', 'rifle', 'pistol', 'handgun', 'shotgun', 'revolver', 'shooting', 'weapon']
gun_crimes = df[df['Description'].str.contains('|'.join(gun_keywords), na=False)]

# === 1. Gun-Related Crime Over Time ===
gun_crimes['YearMonth'] = gun_crimes['Date'].dt.to_period('M')
trend = gun_crimes.groupby('YearMonth').size()

plt.figure(figsize=(12, 6))
trend.plot()
plt.title('Gun-Related Crimes Over Time')
plt.xlabel('Year-Month')
plt.ylabel('Number of Incidents')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# === 2. Primary Types of Gun Crimes ===
plt.figure(figsize=(10, 5))
gun_crimes['Primary Type'].value_counts().head(10).plot(kind='bar')
plt.title('Top Gun-Related Crime Types')
plt.ylabel('Number of Incidents')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# === 3. Arrest Rate for Gun Crimes ===
arrest_rate = gun_crimes['Arrest'].value_counts(normalize=True) * 100
arrest_rate.plot(kind='bar', color=['green', 'red'])
plt.title('Arrest Rate for Gun-Related Crimes')
plt.ylabel('Percentage')
plt.xticks([0, 1], ['Arrested', 'Not Arrested'], rotation=0)
plt.tight_layout()
plt.show()

# === 4. Heatmap (Optional - if you want a map) ===
import folium
from folium.plugins import HeatMap

# Drop rows with missing coordinates
map_data = gun_crimes[['Latitude', 'Longitude']].dropna()

m = folium.Map(location=[map_data['Latitude'].mean(), map_data['Longitude'].mean()], zoom_start=11)
HeatMap(data=map_data[['Latitude', 'Longitude']].values, radius=10).add_to(m)
m.save("gun_crime_heatmap.html")
print("Heatmap saved as 'gun_crime_heatmap.html'.")

# === 5. Day of the Week Analysis ===
gun_crimes.loc[:, 'DayOfWeek'] = gun_crimes['Date'].dt.day_name()
plt.figure(figsize=(8, 4))
sns.countplot(x='DayOfWeek', data=gun_crimes, order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.title('Gun Crimes by Day of the Week')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
