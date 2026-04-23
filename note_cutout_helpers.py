import sys
from NameDictionaries import note_names, hz_to_midi, midi_to_hz, midi_note_offset
from scipy.io import wavfile
import numpy as np
import crepe


def find_notes(data):
    '''Takes in waveform data and outputs a list of tuples where each tuples tells the start and stop sample of a note.'''

    #temp to test note cutout function:
    if data == 'skip':
        return [
            (541171, 1452844),
            (1527089, 2393452),
            (2480297, 3367207),
            (3425218, 4333407),
            (4397930, 5304438),
            (5348180, 6318696),
            (6383180, 7298310),
            (7365100, 8293134),
            (8353464, 9256196),
            (9310696, 10217565),
            (10271182, 11188596),
            (11247028, 12140267),
        ]



    #find {window_size} moving average of amplitudes (based on code from Google Gemini)
    window_size = 7
    moving_average = np.convolve(np.array(data), np.ones(window_size) / window_size, mode='valid')

    rms = np.sqrt(np.mean(np.square(amplitudes)))


def cutout_notes(data, note_list):
    ''' Takes in the data from a wave file and a list of tuples indecating the sample numbers where each note starts and stops.
        Cuts out octave of wave files into individual notes. Returns a dictionary with keys "n" where n is the number of the note
        in the octave. At key n, the dictionary contains the wave file data for that note.'''

    audio_files = {}
    for i in range(len(note_list)):
        audio_files[i] = data[note_list[i][0]:note_list[i][1] + 1]

    return audio_files


def get_pitch(data, sample_rate):
    ''' Takes in audio data and the sample rate for a note, prepares it for Crepe pitch detection, and outputs high confidence pitch by taking mean of confident pitches.'''
    # Convert stereo to mono
    if len(data.shape) == 2:
        data = np.mean(data, axis=1)

    # Convert to float32 and normalize
    data = data.astype(np.float32)
    data = data / np.max(np.abs(data))

    # Get pitch
    time, frequency, confidence, activation = crepe.predict(data, sample_rate)

    high_confidence_pitch = np.mean(frequency[confidence > 0.85])

    return high_confidence_pitch

# TEST COMMENT


def main():
    print(find_notes('skip'))



if __name__ == "__main__":
    main()


