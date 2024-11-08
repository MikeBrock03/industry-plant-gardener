import os
import logging
import requests
import numpy as np
import librosa
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify API credentials
client_id = '7fd502da6b3c4c0497416217aa9eb798'
client_secret = 'ceaf9b84f43042e98ac99935c282f764'

# Initialize Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Directory to save Mel spectrograms
SAVE_DIR = 'mel_spectrograms'

def sanitize_filename(filename):
    """Replace spaces and non-alphanumeric characters with underscores."""
    return re.sub(r'[^\w\-_\. ]', '_', filename.replace(' ', '_'))

def get_preview_url(artist, track):
    """Get the preview URL for a track from Spotify."""
    try:
        results = sp.search(q=f'artist:{artist} track:{track}', type='track')
        if results['tracks']['items']:
            return results['tracks']['items'][0]['preview_url']
    except Exception as e:
        logging.error(f"Error getting preview URL for {artist} - {track}: {e}")
    return None

def download_preview(url, filename):
    """Download the audio preview from the given URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
    except Exception as e:
        logging.error(f"Error downloading preview from {url}: {e}")
    return None

def create_mel_spectrogram(audio_file):
    """Create a Mel spectrogram from an audio file."""
    try:
        y, sr = librosa.load(audio_file)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        return mel_spec_db
    except Exception as e:
        logging.error(f"Error creating Mel spectrogram for {audio_file}: {e}")
    return None

def save_mel_spectrogram(mel_spec, filename):
    """Save the Mel spectrogram as a .npy file."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    filepath = os.path.join(SAVE_DIR, f"{filename}_mel_spec.npy")
    np.save(filepath, mel_spec)
    return filepath

def get_mel_spectrogram_for_track(artist, track):
    """Get the Mel spectrogram for a given track and save it."""
    preview_url = get_preview_url(artist, track)
    if preview_url:
        safe_filename = sanitize_filename(f"{artist}-{track}")
        audio_file = download_preview(preview_url, f"{safe_filename}.mp3")
        if audio_file:
            mel_spec = create_mel_spectrogram(audio_file)
            os.remove(audio_file)  # Clean up the audio file
            if mel_spec is not None:
                saved_file = save_mel_spectrogram(mel_spec, safe_filename)
                logging.info(f"Saved Mel spectrogram to {saved_file}")
                return saved_file
    logging.warning(f"Could not obtain Mel spectrogram for {artist} - {track}")
    return None

def process_track_list(track_list):
    """Process a list of tracks and save their Mel spectrograms."""
    results = {}
    for artist, track in track_list:
        logging.info(f"Processing {artist} - {track}")
        mel_spec_file = get_mel_spectrogram_for_track(artist, track)
        if mel_spec_file is not None:
            results[(artist, track)] = mel_spec_file
    return results

# example input
if __name__ == "__main__":
    # List of (artist, track) tuples to process
    tracks_to_process = [
        ("Hayley Gene Penner", "a good thing")
    ]

    saved_spectrograms = process_track_list(tracks_to_process)

    for (artist, track), file_path in saved_spectrograms.items():
        print(f"Processed {artist} - {track}: Mel spectrogram saved to {file_path}")

    print(f"Successfully processed {len(saved_spectrograms)} out of {len(tracks_to_process)} tracks.")