import numpy as np

# Replace 'path_to_your_file.npy' with the actual path to your .npy file
file_path = 'mel_spectrograms/Hayley_Gene_Penner_Get_Away_mel_spec.npy'

# Load the NumPy array from the file
mel_spectrogram = np.load(file_path)

# Print the shape of the array
print(f"Shape of the Mel spectrogram: {mel_spectrogram.shape}")

# Optionally, print some additional information
print(f"Data type: {mel_spectrogram.dtype}")
print(f"Number of dimensions: {mel_spectrogram.ndim}")
print(f"Total number of elements: {mel_spectrogram.size}")

# If you want to see a small sample of the data (first 5x5 elements, if available)
print("\nSample of the data:")
print(mel_spectrogram)