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

# Filter rows where to exclude non-gun weapons
gun_crimes = gun_crimes[~gun_crimes['Description'].str.contains('knife|blunt|taser|weapon - other', na=False)]

# Removes duplicate rows based on 'ID' column (Assumes 'ID' is a unique identifier for each crime incident)
gun_crimes = gun_crimes.drop_duplicates(subset=['ID'])

# Optionally reset index and preview
gun_crimes = gun_crimes.reset_index(drop=True)
print(gun_crimes.head())

# Classify severity of crime
def classify_severity(crime_type):
	if any(x in crime_type.lower() for x in ['homicide', 'murder']):
		return 'Severe'
	elif any(x in crime_type.lower() for x in ['robbery', 'assault']):
		return 'High'
	else:
		return 'Medium'
        
gun_crimes['Severity'] = gun_crimes['Primary Type'].apply(classify_severity)

# Get day, month, year of crimes
gun_crimes['Year'] = gun_crimes['Date'].dt.year
gun_crimes['Month'] = gun_crimes['Date'].dt.month
gun_crimes['Day'] = gun_crimes['Date'].dt.day
