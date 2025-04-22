import pandas as pd

# Load your CSV file
df = pd.read_csv('Crimes_-_2001_to_Present.csv')  # replace with your actual file path

# List of keywords to identify gun-related crimes
gun_keywords = [
    'gun', 'firearm', 'rifle', 'pistol', 'handgun', 'shotgun',
    'revolver', 'weapon', 'firearms', 'shooting', 'armed'
]

# Convert to lowercase for case-insensitive matching
df['Description'] = df['Description'].astype(str).str.lower()

# Filter rows where any keyword appears in the Description
gun_crimes = df[df['Description'].str.contains('|'.join(gun_keywords), na=False)]

# Optionally reset index and preview
gun_crimes = gun_crimes.reset_index(drop=True)
print(gun_crimes.head())
