import sys
from NameDictionaries import note_names, hz_to_midi, midi_to_hz, midi_note_offset

# grabs settings from CONFIG.txt and assigns them to variables
with open('/workspaces/CS32-final-project/CONFIG.txt') as settings:
    settings_error = False
    try:
        stop_length = settings.readline().split(':')[1].strip()
        midi_offset = midi_note_offset[stop_length]
    except KeyError:
        print('"Stop Length Number" must be a valid length (eg. "8" or "5 1/3"). Please update CONFIG.txt and try again.')
        settings_error = True
    try:
        base_pitch = float(settings.readline().split(':')[1].strip())
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





print(stop_length)
print(midi_offset)
print(base_pitch)
print(tuning_error_margin)
print(num_pipes)
