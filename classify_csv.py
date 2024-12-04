import pandas as pd
import numpy as np
from scipy import stats
import csv

# Read the CSV file with pandas, specifying that there is a header
df = pd.read_csv('raw_data_small.csv', header=0, quotechar='"', escapechar='\\')

# Clean up the data
df['Streams'] = pd.to_numeric(df['Streams'].str.replace(',', ''), errors='coerce')

# Drop any rows where Streams couldn't be converted to a number
df = df.dropna(subset=['Streams'])

# Ensure Streams is integer type
df['Streams'] = df['Streams'].astype(int)

# Group by artist and calculate median and standard deviation
artist_stats = df.groupby('Artist')['Streams'].agg(['median', 'std'])

# Function to classify songs based on stream counts
def classify_song(row, artist_stats):
    median = artist_stats.loc[row['Artist'], 'median']
    std = artist_stats.loc[row['Artist'], 'std']
    z_score = (row['Streams'] - median) / std
    if z_score < -0.5:
        return 0
    elif -0.5 <= z_score < 0.5:
        return 1
    elif 0.5 <= z_score < 1:
        return 2
    else:
        return 3

# Apply classification 
df['Class'] = df.apply(classify_song, axis=1, args=(artist_stats,))

# Save the result
df.to_csv('classified_songs.csv', index=False)