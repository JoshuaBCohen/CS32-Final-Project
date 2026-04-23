# CS32-Final-Project

This is a tool to cut out and name notes from WAVE audio files for use in making digital organ sample sets. The program takes in noise-reduced audio files (files with any background noise removed) containing 12 individual notes. The program cuts out each note by detecting points in the ADSR envelope to determine when the attack begins and when the release has fully reverberated away. It then names each cut out note corresponding to the midi note numbers for the pitch of the note or the octave number given to the program (octave 1 corresponds to midi notes 36-47, octave 2 to midi notes 48-59, octave 3 to midi notes 60-71, octave 4 to midi notes 72-83, octave 5 to midi notes 84-96, octave 6 to midi notes 96-108). For example, middle C would be named 060-c because middle C has the midi note number 60. Tenor G would be 055-g because it is midi note 55. 

To use it, place the python files in a folder with two additional folders called "input_files" and "output_files." Then, place the noise reduced files into the "input_files" folder. Run the script note_cutout.py to cutout the notes. Due to the machine leaning, the cutout process might take time depending on the hardware used. For best results, run locally. 

To run this code, numpy, scipy, crepe, and tensorflow are required. 

