import sys
import os
import numpy as np
from NameDictionaries import note_names, hz_to_midi, midi_to_hz, midi_note_offset
import note_cutout_helpers as helpers
from scipy.io import wavfile
import crepe

# grabs settings from CONFIG.txt and assigns them to variables
with open('CONFIG.txt') as settings:
    settings_error = False
    try:
        stop_length = settings.readline().split(':')[1].strip()
        midi_offset = midi_note_offset[stop_length]
    except KeyError:
        print('"Stop Length Number" must be a valid length (eg. "8" or "5 1/3"). Please update CONFIG.txt and try again.')
        settings_error = True
    try:
        base_pitch = float(settings.readline().split(':')[1].strip())
        base_pitch_offset = base_pitch - 440
    except ValueError:
        print('"Organ Base Pitch" must be a valid float. Please update CONFIG.txt and try again.')
        settings_error = True
    try:
        tuning_error_margin = float(settings.readline().split(':')[1].strip())
    except ValueError:
        print('"Pitch Margin of Error" must be a valid float. Please update CONFIG.txt and try again.')
        settings_error = True
    try:
        num_pipes = int(settings.readline().split(':')[1].strip())
    except ValueError:
        print('"Number of Pipes in Rank" must be a valid integer. Please update CONFIG.txt and try again.')
        settings_error = True
    if settings_error:
        sys.exit(1)

def main():
    # Makes list of files in input_files to be looped through later in main()
    path = 'input_files'
    try:
        dir_list = os.listdir(path)
    except FileNotFoundError:
        print('You must have files in the "input_files" folder.')
        sys.exit(1)

    # Loops through files in dir_list opening each
    for file in dir_list:
        if not file.endswith('.wav'):
            print(f'{file} is not a WAVE file. Skipping it.')
        else:
            # opens input wave file
            samplerate, data = wavfile.read(f'input_files/{file}')

            # uses find_notes() to determine the start and stop of notes
            cutout_samples = helpers.find_notes(data, samplerate)

            # cuts out the the main wave file into smaller wave files in dict notes_dict
            notes_dict = helpers.cutout_notes(data, cutout_samples)

            # ensure output directory exists
            os.makedirs('output_files', exist_ok=True)

            # loops through cutout notes and: pitch detects, finds midi notes with margin of error, and saves notes with appropriate name
            for notes in notes_dict.values():

                # pitch detects using CREPE and normalizes to A = 440 hz tuning
                pitch = helpers.get_pitch(notes, samplerate) + base_pitch_offset

                # convert detected pitch to nearest MIDI note number using formula
                midi_num = helpers.hz_to_midi_number(pitch, 440.0)

                # determines file name and saves note with that name
                if midi_num is None or midi_num == 0:
                    print(f"WARNING: no pitch found (detected {pitch:.1f} Hz). Skipping.")
                else:
                    # optional: warn if pitch is outside tuning error margin
                    if not helpers.validate_pitch(pitch, midi_num, 440.0, tuning_error_margin):
                        expected_hz = midi_to_hz.get(midi_num, 0)
                        print(f"    WARNING: detected {pitch:.1f} Hz is outside +/-{tuning_error_margin}% of expected {expected_hz:.1f} Hz for MIDI {midi_num}. Proceeding anyway.")

                    file_name = note_names[midi_num + midi_offset]
                    wavfile.write(f"output_files/{file_name}.wav", samplerate, notes)

if __name__ == "__main__":
    main()



