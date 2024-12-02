import os
import logging
import requests
import numpy as np
import librosa
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directory to save Mel spectrograms
SAVE_DIR = 'mel_spectrograms'

def sanitize_filename(filename):
    """Replace spaces and non-alphanumeric characters with underscores."""
    return re.sub(r'[^\w\-_\. ]', '_', filename.replace(' ', '_'))

def search_track(artist, track):
    """Search for a track on Deezer using the advanced search."""
    try:
        query = f'artist:"{artist}" track:"{track}"'
        url = f'https://api.deezer.com/search?q={query}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            track_info = data['data'][0]
            return {
                'preview_url': track_info.get('preview'),
                'title': track_info.get('title'),
                'artist': track_info.get('artist', {}).get('name'),
                'duration': track_info.get('duration')
            }
    except Exception as e:
        logging.error(f"Error searching for {artist} - {track}: {e}")
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
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, hop_length = 1024, n_mels = 80, n_fft = 1024) #default is hop_length = 512, n_mels = 120, n_fft = 2048
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
    track_info = search_track(artist, track)
    if track_info and track_info['preview_url']:
        safe_filename = sanitize_filename(f"{artist}-{track}")
        audio_file = download_preview(track_info['preview_url'], f"{safe_filename}.mp3")
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

# Example usage
if __name__ == "__main__":
    # List of (artist, track) tuples to process
    tracks_to_process = [
        ("Hayley Gene Penner", "a good thing")
    ]

    saved_spectrograms = process_track_list(tracks_to_process)

    for (artist, track), file_path in saved_spectrograms.items():
        print(f"Processed {artist} - {track}: Mel spectrogram saved to {file_path}")

    print(f"Successfully processed {len(saved_spectrograms)} out of {len(tracks_to_process)} tracks.")