import os
import glob
import re
from pathlib import Path
import argparse

def sanitize_filename(filename):
    """Replace spaces and non-alphanumeric characters with underscores."""
    return re.sub(r'[^\w\-_\. ]', '_', filename.replace(' ', '_'))

def cleanup_spectrograms(dry_run=True):
    # Get all mel spectrogram files
    mel_specs = glob.glob('mel_spectrograms/*.npy')
    
    # Track files
    to_delete = []
    
    for mel_spec in mel_specs:
        # Extract base name (everything before _mel_spec.npy)
        base_name = Path(mel_spec).name.replace('_mel_spec.npy', '')
        
        # Check both original and converted filenames in lyrics directories
        lyrics_files = glob.glob('lyrics/*')
        processed_lyrics_files = glob.glob('processed_lyrics/*')
        
        # Convert found files to mel_spec format for comparison
        lyrics_found = False
        processed_found = False
        
        # Check lyrics files
        for lyrics_file in lyrics_files:
            # Apply the same sanitization to lyrics filename
            lyrics_base = sanitize_filename(Path(lyrics_file).stem)
            if lyrics_base == base_name:
                lyrics_found = lyrics_file
                break
                
        # Check processed lyrics files
        for proc_file in processed_lyrics_files:
            # Apply the same sanitization to processed lyrics filename
            proc_base = sanitize_filename(Path(proc_file).stem.replace('_bert', ''))
            if proc_base == base_name:
                processed_found = proc_file
                break
        
        # If either file is missing
        if not (lyrics_found and processed_found):
            print(f"Found unpaired spectrogram: {mel_spec}")
            if not lyrics_found:
                print(f"Missing lyrics file")
            else:
                print(f"Found lyrics: {lyrics_found}")
            
            if not processed_found:
                print(f"Missing processed lyrics file")
            else:
                print(f"Found processed: {processed_found}")
            print()  # Empty line for readability
            to_delete.append(mel_spec)
    
    # Summary
    print(f"\nSummary:")
    print(f"Found {len(to_delete)} mel spectrograms without matching lyrics files")
    
    if not dry_run and to_delete:
        print("\nProceeding with deletion...")
        for file in to_delete:
            os.remove(file)
            print(f"Deleted: {file}")
        print(f"\nDeletion complete: {len(to_delete)} files removed")
    elif to_delete:
        print("\nDRY RUN - No files were actually deleted")
        print("To perform the actual deletion, run the script with --execute flag")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clean up unpaired mel spectrograms')
    parser.add_argument('--execute', action='store_true', 
                      help='Execute actual deletion. Without this flag, runs in dry-run mode')
    args = parser.parse_args()
    
    cleanup_spectrograms(dry_run=not args.execute)