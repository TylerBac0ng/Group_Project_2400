import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset (only necessary columns)
df = pd.read_csv('Crimes_-_2001_to_Present.csv', usecols=[
    'Date', 'Primary Type', 'Description', 'Arrest', 'District', 'Community Area'
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

# Add Year column
gun_crimes['Year'] = gun_crimes['Date'].dt.year

# --- Reduce the data to manageable size ---
# Optional: if gun_crimes still has >100k rows, sample down
if len(gun_crimes) > 50000:
    gun_crimes = gun_crimes.sample(50000, random_state=1)

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

# 3. Box Plot: Top 10 Districts with Most Gun Crimes
top_districts = gun_crimes['District'].value_counts().nlargest(10).index
plt.figure(figsize=(12,6))
sns.boxplot(x='District', y='Year', data=gun_crimes[gun_crimes['District'].isin(top_districts)])
plt.title('Distribution of Gun Crimes by Top Districts')
plt.xlabel('Police District')
plt.ylabel('Year')
plt.tight_layout()
plt.show()

# 4. Violin Plot: Top 10 Community Areas
top_areas = gun_crimes['Community Area'].value_counts().nlargest(10).index
plt.figure(figsize=(14,6))
sns.violinplot(x='Community Area', y='Year', data=gun_crimes[gun_crimes['Community Area'].isin(top_areas)], inner='quartile')
plt.title('Gun Crime Distribution in Top Community Areas')
plt.xlabel('Community Area')
plt.ylabel('Year')
plt.tight_layout()
plt.show()

# 5. Trendline: Year vs Number of Gun Crimes
crime_trend = gun_crimes.groupby('Year').size().reset_index(name='Crime Count')
plt.figure(figsize=(10,5))
sns.regplot(x='Year', y='Crime Count', data=crime_trend, scatter=True, ci=None, line_kws={"color": "red"})
plt.title('Gun Crime Trend Over Years')
plt.xlabel('Year')
plt.ylabel('Number of Gun Crimes')
plt.tight_layout()
plt.show()
