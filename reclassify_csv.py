import pandas as pd
import numpy as np

def compute_artist_relative_score(streams, artist_streams):
    if len(artist_streams) <= 1:
        return 1.5
    
    # Log transform streams
    log_streams = np.log1p(streams)
    log_artist_streams = np.log1p(artist_streams)
    
    # Calculate artist-specific log statistics
    log_median = np.median(log_artist_streams)
    log_std = np.std(log_artist_streams)
    
    if log_std == 0:
        return 1.5
    
    # Compute z-score in log space
    z_score = (log_streams - log_median) / log_std
    
    # Instead of tanh, use a piece-wise scaling function
    # This gives more control over the distribution
    def scale_score(z):
        if z <= -2:
            return 0.25 * (z + 2)  # Linear scaling for very low scores
        elif z >= 2:
            return 3 - 0.25 * (6 - z)  # Linear scaling for very high scores
        else:
            # Smooth scaling in the middle range
            return 1.5 + (0.75 * z)
    
    scaled_score = scale_score(z_score)
    
    # Ensure bounds
    return np.clip(scaled_score, 0, 3)

def reclassify_songs(file_path):
    # Read the existing preprocessed data
    df = pd.read_csv(file_path)
    
    # Calculate new scores for each artist's songs
    new_scores = []
    
    # Process each artist's songs
    for artist in df['Artist'].unique():
        artist_mask = df['Artist'] == artist
        artist_streams = df.loc[artist_mask, 'Streams'].values
        
        # Calculate scores for all songs of this artist
        artist_scores = [compute_artist_relative_score(streams, artist_streams) 
                        for streams in artist_streams]
        new_scores.extend(artist_scores)
    
    # Update the Class column
    df['Class'] = new_scores
    
    # Save back to the same file
    df.to_csv(file_path, index=False)
    
    # Print statistics
    print("\nNew Class Score Distribution:")
    print(f"Mean: {df['Class'].mean():.4f}")
    print(f"Std: {df['Class'].std():.4f}")
    print(f"Min: {df['Class'].min():.4f}")
    print(f"Max: {df['Class'].max():.4f}")
    
    # Print detailed percentile information
    percentiles = [0, 5, 10, 25, 50, 75, 90, 95, 100]
    print("\nPercentile Distribution:")
    for p in percentiles:
        print(f"{p}th percentile: {np.percentile(df['Class'], p):.4f}")

if __name__ == "__main__":
    file_path = 'new_classified_songs.csv'
    print("Updating class scores in", file_path)
    reclassify_songs(file_path)