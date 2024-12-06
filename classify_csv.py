import pandas as pd
import numpy as np
from scipy import stats

# Read the CSV file with pandas, specifying that there is a header
df = pd.read_csv('raw_data.csv', header=0, quotechar='"', escapechar='\\')

# Clean up the data
df['Streams'] = pd.to_numeric(df['Streams'].str.replace(',', ''), errors='coerce')

# Drop any rows where Streams couldn't be converted to a number
df = df.dropna(subset=['Streams'])

# Ensure Streams is integer type
df['Streams'] = df['Streams'].astype(int)

# Group by artist and calculate median and standard deviation
artist_stats = df.groupby('Artist')['Streams'].agg(['median', 'std'])

# Function to compute z-score for songs
def compute_z_score(row, artist_stats):
    median = artist_stats.loc[row['Artist'], 'median']
    std = artist_stats.loc[row['Artist'], 'std']
    if std == 0:
        return 0  # To handle cases where std is zero
    z_score = (row['Streams'] - median) / std
    return z_score

# Apply z-score computation
z_score = df.apply(compute_z_score, axis=1, args=(artist_stats,))

min_z = z_score.min()
max_z = z_score.max()

# Min-max normalization to scale to [0, 3], replacing Class (could also be like Scaled_Score or something)
if max_z != min_z:  # Ensure min and max are not equal
    df['Class'] = 3 * (z_score - min_z) / (max_z - min_z)
else:
    df['Class'] = 0  # If all Z_Score values are the same

# Save the result
df.to_csv('classified_songs.csv', index=False)