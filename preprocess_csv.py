import os
import numpy as np
import lyricsgenius
import pandas as pd
from tqdm import tqdm
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from joblib import dump, load
from gather_mel_spec import get_mel_spectrogram_for_track
import requests
from bs4 import BeautifulSoup
import time
from typing import Optional, Dict
import json
import urllib.parse
import torch
from transformers import BertTokenizer, BertModel

# No longer using the Genius API

LYRICS_DIR = 'lyrics'
PROCESSED_LYRICS_DIR = 'processed_lyrics'

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

if not os.path.exists(LYRICS_DIR):
    os.makedirs(LYRICS_DIR)

df = pd.read_csv('classified_songs.csv', header=0, quotechar='"', escapechar='\\')

def get_lyrics(artist: str, song: str) -> str:
    """
    Scrape lyrics from Genius. Returns '[NO_LYRICS]' if lyrics cannot be found.
    """
    # Search for the song
    query = f"{artist} {song}"
    search_url = f"https://genius.com/api/search/song?q={urllib.parse.quote(query)}"
    
    try:
        # Add a small delay to be nice to Genius
        time.sleep(1)
        
        # Get the song URL
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            hits = data.get('response', {}).get('sections', [{}])[0].get('hits', [])
            if not hits:
                print(f"No results found for: {query}")
                return "[NO_LYRICS]"
            
            url = hits[0]['result']['url']
            
            # Get the lyrics page
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                lyrics_container = soup.select_one('div[class*="Lyrics__Container"]')
                if lyrics_container:
                    # Remove script tags
                    for script in lyrics_container.find_all('script'):
                        script.decompose()
                    
                    # Get text and clean it
                    lyrics = lyrics_container.get_text()
                    cleaned_lyrics = clean_lyrics(lyrics)
                    
                    # Check if we actually got lyrics after cleaning
                    if cleaned_lyrics.strip():
                        return cleaned_lyrics
        
        print(f"Could not get lyrics for: {query}")
        return "[NO_LYRICS]"
            
    except Exception as e:
        print(f"Error getting lyrics for {artist} - {song}: {e}")
        return "[NO_LYRICS]"

def clean_lyrics(lyrics):
    # Remove the "X Contributors" line
    lyrics = re.sub(r'^.*?Contributors.*?\n', '', lyrics, flags=re.MULTILINE)
    
    # # Remove anything in brackets like [chorus] 
    lyrics = re.sub(r'\[.*?\]', ' ', lyrics)

    
    return lyrics
    
def save_lyrics(artist, song, lyrics, tokenizer, model):
    """
    Save both raw lyrics and BERT processed features
    Returns paths to both files
    """
    # Save raw lyrics
    raw_file_name = f"{artist}-{song}.txt".replace(" ", "_").replace("/", "_")
    raw_file_path = os.path.join(LYRICS_DIR, raw_file_name)
    
    with open(raw_file_path, 'w', encoding='utf-8') as f:
        f.write(lyrics)
    
    # Save processed features if lyrics exist
    if lyrics:
        with torch.no_grad(): #prevents it from calculating a bunch of unecessary gradients
            tokens = tokenizer(lyrics, return_tensors='pt', padding=True, truncation=True) #Split lyrics into tokens
            outputs = model(**tokens) #turn the tokens into a bunch of useful data structures
            cls_embedding = outputs.last_hidden_state[:, 0, :].numpy()  #get the structure we want! acts as features we can use in linear regression

        #save processed lyrics
        processed_file_name = f"{artist}-{song}_bert.npy".replace(" ", "_").replace("/", "_")
        processed_file_path = os.path.join(PROCESSED_LYRICS_DIR, processed_file_name)
        np.save(processed_file_path, cls_embedding)
        
        return raw_file_path, processed_file_path
    
    return raw_file_path, None

# Directory to save Mel spectrograms
MEL_SPEC_DIR = 'mel_spectrograms'
if not os.path.exists(MEL_SPEC_DIR):
    os.makedirs(MEL_SPEC_DIR)

# Process each song
print("Processing songs with BERT (shoutout)...")
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing songs"):
    artist = row['Artist']
    song = row['Song']
    
    # Get Mel spectrogram
    mel_spec_file = get_mel_spectrogram_for_track(artist, song)
    if mel_spec_file:
        df.at[index, 'Mel_Spectrogram'] = mel_spec_file
    
    # Get and save lyrics with BERT processing
    lyrics = get_lyrics(artist, song)
    if lyrics:
        raw_lyrics_path, processed_lyrics_path = save_lyrics(artist, song, lyrics, tokenizer, model)
        df.at[index, 'Lyrics_File'] = raw_lyrics_path
        df.at[index, 'Processed_Lyrics_File'] = processed_lyrics_path
    else:
        df.at[index, 'Lyrics_File'] = ''
        df.at[index, 'Processed_Lyrics_File'] = ''

# Save the updated dataframe
df.to_csv('preprocessed_data.csv', index=False)

print("Processing complete! Data saved to 'preprocessed_data.csv'")
print(f"BERT vectorizer saved to {PROCESSED_LYRICS_DIR}/tfidf_vectorizer.joblib")