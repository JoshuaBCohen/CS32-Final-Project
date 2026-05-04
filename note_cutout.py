import sys
from NameDictionaries import note_names, hz_to_midi, midi_to_hz, midi_note_offset
import note_cutout_helpers as helpers
from scipy.io import wavfile
import os
import crepe
import numpy as np
import tkinter as tk
from tkinter.filedialog import askdirectory
tk.Tk().withdraw() # part of the import if you are not using other tkinter functions

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
        base_pitch_offset = 440 - base_pitch
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
    GPU_setting = settings.readline().split(':')[1].strip().lower()
    if GPU_setting == 'y':
        GPU_acceleration = True
    elif GPU_setting == 'n':
        GPU_acceleration = False
    else:
        print('"GPU acceleration must be either "Y" or "n."')
        settings_error = True
    if settings_error:
        sys.exit(1)

if not GPU_acceleration:
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1' #runs on cpu

def main():
    num_notes_saved = 0
    # Asks user for input and output folder and checks to makesure a path was entered
    path = askdirectory(title='Choose folder containing input files')
    if path == '':
        sys.exit('No input folder chosen. Exiting.')
    output_folder = askdirectory(title='Choose output folder')
    if output_folder == '':
        sys.exit('No output folder chosen. Exiting.')

    # Makes list of files in input_files to be looped through later in main()
    try:
        dir_list = os.listdir(path)
    except FileNotFoundError:
        print('You must have files in the "input_files" folder.')
        sys.exit(1)

    # Loops through files in dir_list opening each
    for file in dir_list:
        if not file.lower().endswith('.wav'):
            print(f'{file} is not a WAVE file. Skipping it.')
        else:
            # opens input wave file
            samplerate, data = wavfile.read(os.path.join(path, file))

            # uses find_notes() to determine the start and stop of notes
            cutout_samples = helpers.find_notes(data, samplerate)

            # cuts out the the main wave file into smaller wave files in dict notes_dict
            notes_dict = helpers.cutout_notes(data, cutout_samples)

            # loops through cutout notes and: pitch detects, finds midi notes with margin of error, and saves notes with appropriate name
            for notes in notes_dict.values():

                # pitch detects and makes tuple with pitch margins of error
                pitch = helpers.get_pitch(notes, samplerate) + base_pitch_offset # pitch normalized to A = 440 hz tuning
                pitch_error = (pitch + pitch * tuning_error_margin / 100), (pitch - pitch * tuning_error_margin / 100)

                # loops through hz_to_midi to find appropriate midi note number
                midi_num = 0
                for frequencies, midi in hz_to_midi.items():
                    if frequencies > pitch_error[1] and frequencies < pitch_error[0]:
                        midi_num = midi
                        break

                # determines file name and saves note with that name
                if midi_num == 0:
                    print("WARNING: no pitch found. Skipping.")
                else:
                    file_name = note_names[midi_num + midi_offset]
                    print(f'Saving {file_name}...')
                    wavfile.write(os.path.join(output_folder, f"{file_name}.wav"), samplerate, notes)
                    num_notes_saved += 1
    if num_notes_saved != num_pipes:
        print(f'Program skipped {num_pipes - num_notes_saved} notes.')

if __name__ == "__main__":
    main()



