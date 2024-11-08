import os
import numpy as np
import lyricsgenius
import pandas as pd
from tqdm import tqdm
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import dump, load
from gather_mel_spec import get_mel_spectrogram_for_track

# Initialize Genius API client
client = 'pMZWtW9FlaIkiHMWUQsB86MOCEOxCBI9thVUG2ezEIsDIMH7sRukQCKZGrOVQh6c'
client_secret = 'fPMW_XfjYprM7QE1x5DwzObZsmieOW7FFoZC7Rq3FQt_QBwEFmzWuhkIJIOG8OnB-bDCRK7rC_BAP2ZLWwFtSA'
access_token = 'sUezPRZv-5UwFx58YwOPWDknftwAUem8_ZN9okCVeq0yfWQQLkUO3r-45f0OarCo'

genius = lyricsgenius.Genius(access_token)

LYRICS_DIR = 'lyrics'
PROCESSED_LYRICS_DIR = 'processed_lyrics'
if not os.path.exists(LYRICS_DIR):
    os.makedirs(LYRICS_DIR)

def clean_lyrics(lyrics):
    # Remove the "X Contributors" line
    lyrics = re.sub(r'^.*?Contributors.*?\n', '', lyrics, flags=re.MULTILINE)
    
    # # Remove anything in brackets like [chorus] - TODO: ask team
    # lyrics = re.sub(r'\[.*?\]', '', lyrics)
    
    # Remove empty lines and strip whitespace
    lyrics = '\n'.join([line.strip() for line in lyrics.split('\n') if line.strip()])
    
    return lyrics

def get_lyrics(artist, song):
    try:
        song = genius.search_song(song, artist)
        if song:
            return clean_lyrics(song.lyrics)
        else:
            return ""
    except Exception as e:
        print(f"Error getting lyrics for {artist} - {song}: {e}")
        return ""
    
def save_lyrics(artist, song, lyrics, vectorizer=None):
    """
    Save both raw lyrics and TF-IDF processed features
    Returns paths to both files
    """
    # Save raw lyrics
    raw_file_name = f"{artist}-{song}.txt".replace(" ", "_").replace("/", "_")
    raw_file_path = os.path.join(LYRICS_DIR, raw_file_name)
    
    with open(raw_file_path, 'w', encoding='utf-8') as f:
        f.write(lyrics)
    
    # Save processed features if vectorizer is provided
    if vectorizer and lyrics:
        processed_file_name = f"{artist}-{song}_tfidf.npy".replace(" ", "_").replace("/", "_")
        processed_file_path = os.path.join(PROCESSED_LYRICS_DIR, processed_file_name)
        
        # Transform lyrics to TF-IDF features
        features = vectorizer.transform([lyrics]).toarray()
        np.save(processed_file_path, features)
        
        return raw_file_path, processed_file_path
    
    return raw_file_path, None
