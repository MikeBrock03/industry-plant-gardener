import os
import numpy as np
import lyricsgenius
import pandas as pd
from tqdm import tqdm
import re
import torch
from joblib import dump, load
from transformers import BertTokenizer, BertModel
from gather_mel_spec import get_mel_spectrogram_for_track

# Initialize Genius API client
client = 'pMZWtW9FlaIkiHMWUQsB86MOCEOxCBI9thVUG2ezEIsDIMH7sRukQCKZGrOVQh6c'
client_secret = 'fPMW_XfjYprM7QE1x5DwzObZsmieOW7FFoZC7Rq3FQt_QBwEFmzWuhkIJIOG8OnB-bDCRK7rC_BAP2ZLWwFtSA'
access_token = 'sUezPRZv-5UwFx58YwOPWDknftwAUem8_ZN9okCVeq0yfWQQLkUO3r-45f0OarCo'

genius = lyricsgenius.Genius(access_token)

LYRICS_DIR = 'lyrics'
PROCESSED_LYRICS_DIR = 'processed_lyrics'

# Load BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.eval()

if not os.path.exists(LYRICS_DIR):
    os.makedirs(LYRICS_DIR)

df = pd.read_csv('processed_and_classified_songs.csv', header=0, quotechar='"', escapechar='\\')

def clean_lyrics(lyrics):
    # Remove the "X Contributors" line
    lyrics = re.sub(r'^.*?Contributors.*?\n', '', lyrics, flags=re.MULTILINE)
    
    # Remove anything in brackets like [chorus] (good idea Michael)
    lyrics = re.sub(r'\[.*?\]', '', lyrics)

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
    
def save_lyrics(artist, song, lyrics, tokenizer, model):
    """
    Save both raw lyrics and TF-IDF processed features
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
#print(f"TF-IDF vectorizer saved to {PROCESSED_LYRICS_DIR}/tfidf_vectorizer.joblib")