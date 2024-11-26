import streamlit as st
import numpy as np
import random
from pydub import AudioSegment
import soundfile as sf  # Replaced simpleaudio with soundfile

# Define notes with frequencies (Hz) and their corresponding WAV file names
notes = {
    "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, 
    "G4": 392.00, "A4": 440.00, "B4": 493.88, "C5": 523.25
}

# Harmony Search parameters
HMS = 5  # Harmony Memory Size
HMCR = 0.9  # Harmony Memory Consideration Rate
PAR = 0.3  # Pitch Adjustment Rate
num_iterations = 100  # Number of iterations
sequence_length = 10  # Length of the note sequence to make it around 10 seconds

# Streamlit input for sequence length
n = st.sidebar.text_input("Sequence Length", "10")
if n: 
    sequence_length = int(n)
    st.sidebar.write(f"Music length: {sequence_length}")

# Objective function with improvements
def objective_function(note_sequence):
    total_freq = sum(notes[note] for note in note_sequence)
    freq_diff = abs(total_freq - 440.00)  # Target A4 frequency
    penalty = 0
    
    # Add penalty for consecutive repetitions
    for i in range(1, len(note_sequence)):
        if note_sequence[i] == note_sequence[i - 1]:
            penalty += 50  # Increase penalty value as needed
            
    # Reward for harmonic intervals
    ideal_intervals = [2, 4, 7]  # semitones: major second, major third, perfect fifth
    for i in range(1, len(note_sequence)):
        interval = abs(list(notes.keys()).index(note_sequence[i]) - list(notes.keys()).index(note_sequence[i-1]))
        if interval in ideal_intervals:
            penalty -= 20  # Reward for harmonic interval

    return freq_diff + penalty

# Initialize Harmony Memory (HM)
def initialize_harmony_memory():
    return [random.choices(list(notes.keys()), k=sequence_length) for _ in range(HMS)]

# Harmony Search Algorithm with improved objective
def harmony_search(harmony_memory):
    for iteration in range(num_iterations):
        new_harmony = []
        for i in range(sequence_length):  # Sequence length of 10 notes
            if random.random() < HMCR:
                new_harmony.append(random.choice(random.choice(harmony_memory)))
            else:
                new_harmony.append(random.choice(list(notes.keys())))
                
            # Pitch adjustment
            if random.random() < PAR:
                new_harmony[i] = random.choice(list(notes.keys()))
        
        # Evaluate and update harmony memory if better
        if objective_function(new_harmony) < objective_function(harmony_memory[-1]):
            harmony_memory[-1] = new_harmony
            harmony_memory = sorted(harmony_memory, key=objective_function)
    return harmony_memory

# Function to play a note
def play_note(note):
    # Use soundfile to read and play the WAV files
    data, samplerate = sf.read(f"{note}.wav")
    sf.write("temp.wav", data, samplerate)  # Temporary write to file to play
    st.audio("temp.wav")

# Function to play the best harmony
def play_harmony(note_sequence):
    harmony = AudioSegment.from_wav(f"{note_sequence[0]}.wav")
    for note in note_sequence[1:]:
        sound = AudioSegment.from_wav(f"{note}.wav")
        harmony += sound
    harmony.export("best_harmony.wav", format="wav")
    
    # Using soundfile to read and play the best harmony
    data, samplerate = sf.read("best_harmony.wav")
    sf.write("temp_best_harmony.wav", data, samplerate)  # Temporary write to file to play
    st.audio("temp_best_harmony.wav")

# Streamlit UI
st.header("Simple Piano with Harmony Search 🎹")
st.image("piano.png", use_container_width=True)

# Create a simple piano interface
st.title("Click on a note to play it 🎧")

# Display buttons for each note in one row
cols = st.columns(len(notes))
for i, note in enumerate(notes.keys()):
    with cols[i]:
        if st.button(note):
            play_note(note)

# Create three columns to center the "Generate Best Harmony" button
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("Generate Best Harmony 🎼"):
        harmony_memory = initialize_harmony_memory()
        best_harmony = harmony_search(harmony_memory)
        best_harmony_sequence = best_harmony[0]
        st.write("Best Note Sequence:", best_harmony_sequence)
        
        # Play the best harmony (note: this will only work if the .wav files are present)
        play_harmony(best_harmony_sequence)
        
        st.audio("temp_best_harmony.wav")
