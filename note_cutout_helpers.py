import sys
import math
from NameDictionaries import note_names, hz_to_midi, midi_to_hz, midi_note_offset
from scipy.io import wavfile
import numpy as np
import librosa
import crepe


def find_notes(data, samplerate):
    '''Takes in waveform data and sample rate, detects note boundaries using
    RMS energy thresholding, and outputs a list of tuples where each tuple
    tells the start and stop sample of a note.'''

    # Convert raw integer audio data to float32 mono for RMS analysis
    audio = data.astype(np.float32)
    if len(audio.shape) == 2:
        audio = np.mean(audio, axis=1)
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val

    # Compute RMS energy envelope using librosa
    hop_length = 512
    rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]

    # Detect note boundaries from the RMS envelope
    boundaries = detect_note_boundaries(
        rms, samplerate, hop_length,
        silence_threshold_ratio=0.02,
        min_note_duration=0.15,
        min_silence_duration=0.25,
        attack_pad_seconds=0.05,
        release_pad_seconds=0.15,
    )

    # Clamp boundaries to valid audio range
    total_samples = len(data)
    boundaries = [
        (max(0, s), min(total_samples, e))
        for s, e in boundaries
    ]

    print(f'    Detected {len(boundaries)} note(s).')
    return boundaries


def cutout_notes(data, note_list):
    ''' Takes in the data from a wave file and a list of tuples indecating the sample numbers where each note starts and stops.
        Cuts out octave of wave files into individual notes. Returns a dictionary with keys "n" where n is the number of the note
        in the octave. At key n, the dictionary contains the wave file data for that note.'''
    '''code note cutouts and what we the need input and output to be'''

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


# ---------------------------------------------------------------------------
# New helper functions (integrated from AI-generated boundary detection script)
# ---------------------------------------------------------------------------

def detect_note_boundaries(rms_energy, sr, hop_length,
                           silence_threshold_ratio=0.02,
                           min_note_duration=0.1,
                           min_silence_duration=0.3,
                           attack_pad_seconds=0.05,
                           release_pad_seconds=0.1):
    '''Detect note start and end boundaries from an RMS energy envelope.

    Algorithm:
    1. Threshold the RMS energy to find "active" vs "silent" frames.
    2. Group contiguous active frames into note regions.
    3. Merge regions separated by very short silence (brief dips in sustained notes).
    4. Filter out regions shorter than min_note_duration.
    5. Pad each region to preserve attack transient and reverb tail.

    Args:
        rms_energy: 1D numpy array of RMS energy values per frame.
        sr: Audio sample rate.
        hop_length: Number of audio samples per RMS frame.
        silence_threshold_ratio: Fraction of max RMS to use as silence threshold.
        min_note_duration: Minimum note length in seconds (shorter = noise artifact).
        min_silence_duration: Minimum silence gap in seconds to split notes.
        attack_pad_seconds: Seconds to pad before each note's detected start.
        release_pad_seconds: Seconds to pad after each note's detected end.

    Returns:
        A list of (start_sample, end_sample) tuples.
    '''
    threshold = np.max(rms_energy) * silence_threshold_ratio
    is_active = rms_energy > threshold

    # Find contiguous active regions
    regions = []
    in_region = False
    start_frame = 0

    for i, active in enumerate(is_active):
        if active and not in_region:
            start_frame = i
            in_region = True
        elif not active and in_region:
            regions.append((start_frame, i - 1))
            in_region = False

    # Close any region that extends to the end
    if in_region:
        regions.append((start_frame, len(is_active) - 1))

    if not regions:
        return []

    # Merge regions separated by very short silence
    min_silence_frames = int(min_silence_duration * sr / hop_length)
    merged = [regions[0]]
    for start, end in regions[1:]:
        prev_start, prev_end = merged[-1]
        if start - prev_end < min_silence_frames:
            # Merge with previous region
            merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    # Convert frames to samples and apply padding
    attack_pad_samples = int(attack_pad_seconds * sr)
    release_pad_samples = int(release_pad_seconds * sr)
    min_note_samples = int(min_note_duration * sr)

    note_boundaries = []
    for start_frame, end_frame in merged:
        start_sample = max(0, start_frame * hop_length - attack_pad_samples)
        end_sample = end_frame * hop_length + release_pad_samples

        # Filter out very short regions (noise artifacts)
        if (end_sample - start_sample) >= min_note_samples:
            note_boundaries.append((start_sample, end_sample))

    return note_boundaries


def hz_to_midi_number(freq, base_pitch=440.0):
    '''Convert a frequency in Hz to the nearest MIDI note number.

    Uses the standard formula: midi = 69 + 12 * log2(freq / base_pitch)
    This works with any base pitch (not just A440) and handles the
    imprecise frequencies returned by pitch detection algorithms.

    Args:
        freq: Detected frequency in Hz.
        base_pitch: The tuning reference pitch for A4 (default 440 Hz).

    Returns:
        The nearest MIDI note number as an integer, or None if freq is invalid.
    '''
    if freq <= 0 or np.isnan(freq):
        return None
    midi_float = 69 + 12 * math.log2(freq / base_pitch)
    return round(midi_float)


def validate_pitch(detected_hz, expected_midi, base_pitch=440.0, margin_percent=1.0):
    '''Check whether a detected pitch is within an acceptable margin of error
    of the expected MIDI note's true frequency.

    Args:
        detected_hz: The frequency detected by pitch analysis (Hz).
        expected_midi: The MIDI note number we expect this note to be.
        base_pitch: The tuning reference pitch for A4 (default 440 Hz).
        margin_percent: Acceptable deviation as a percentage (e.g., 1.0 = +/-1%).

    Returns:
        True if the detected pitch is within the margin, False otherwise.
    '''
    if expected_midi not in midi_to_hz:
        return False

    # Compute expected frequency from the MIDI number using the base pitch
    # midi_to_hz is based on A440, so we scale if base_pitch differs
    expected_hz_a440 = midi_to_hz[expected_midi]
    scale_factor = base_pitch / 440.0
    expected_hz = expected_hz_a440 * scale_factor

    deviation_percent = abs(detected_hz - expected_hz) / expected_hz * 100
    return deviation_percent <= margin_percent


def main():
    print('note_cutout_helpers.py — run note_cutout.py to process files.')


if __name__ == "__main__":
    main()


