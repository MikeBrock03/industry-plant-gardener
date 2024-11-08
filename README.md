# industry plant gardener

# Music Classification and Analysis Pipeline

This repository contains a pipeline for processing music data, extracting features, and preparing it for analysis in Google Colab.

## Overview

The pipeline processes music data through multiple stages:
1. Initial song classification
2. Feature extraction (lyrics, mel spectrograms)
3. Data preprocessing for machine learning

## Prerequisites

- Python 3.12.7+
- All of the packages that come in as imports (will become requirements.txt soon :D)
- Required input file: `raw_data.csv` with columns:
  - Artist
  - Song
  - Streams
  - Genre

## Pipeline Steps

### 1. Song Classification

Run the classification script to categorize each song:

```bash
python classify_csv.py
```

This creates `processed_and_classified_songs.csv` from `raw_data.csv` (input filename is currently hardcoded).

### 2. Feature Extraction & Preprocessing

Run the preprocessing script to extract features:

```bash
python preprocess_csv.py
```

This script:
- Uses `processed_and_classified_songs.csv` as input (hardcoded)
- Generates the following outputs:
  - `preprocessed_data.csv`
  - Lyrics in the `lyrics/` folder
  - Mel spectrograms in the `mel_spectrograms/` folder
  - Processed lyrics vectors in `processed_lyrics/` folder

### 3. Google Colab Setup

1. Upload the following files to your shared Google Drive:
   - `preprocessed_data.csv`
   - Contents of `lyrics/` folder
   - Contents of `mel_spectrograms/` folder
   - Contents of `processed_lyrics/` folder

2. Open and run the provided Google Colab notebook

## Project Structure

```
.
├── raw_data.csv                        # Initial input data
├── classify_csv.py                     # Song classification script
├── preprocess_csv.py                   # Feature extraction script
├── processed_and_classified_songs.csv  # Classification output
├── preprocessed_data.csv               # Final preprocessed data
├── lyrics/                            # Extracted lyrics
├── mel_spectrograms/                  # Generated spectrograms
└── processed_lyrics/                  # Vectorized lyrics
```

## Notes

- Input filenames are currently hardcoded in the scripts
- Other files in the repository were used for testing purposes
- Ensure all generated files are uploaded to the shared Google Drive before running the Colab notebook

## Future Improvements

- Make input/output filenames configurable via command line arguments
- Add error handling for missing files/folders
