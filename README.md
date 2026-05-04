# CS32-Final-Project

This is a tool to cut out and name notes from WAVE audio files for use in making digital organ sample sets. The program takes in noise-reduced audio files (files with any background noise removed) containing 12 individual notes. The program cuts out each note by detecting points in the ADSR envelope to determine when the attack begins and when the release has fully reverberated away. It then names each cut out note corresponding to the midi note numbers for the pitch of the note or the octave number given to the program (octave 1 corresponds to midi notes 36-47, octave 2 to midi notes 48-59, octave 3 to midi notes 60-71, octave 4 to midi notes 72-83, octave 5 to midi notes 84-96, octave 6 to midi notes 96-108). For example, middle C would be named 060-c because middle C has the midi note number 60. Tenor G would be 055-g because it is midi note 55. 

We used GenAI to troubleshoot when we were experiencing syntax errors and we used it to help guide us on how to work through issues with github and in the terminal, such as git control and the commands. 

We did research on audio processing tools and settled on using librosa. Root mean squared was the simplest approach to cutting out notes since our files were already noise-reduced, so we were able to implement RMS manually. GenAI helped us implement the # Clamp boundaries to valid audio range:/
&emsp;total_samples = len(data)\
&emsp;boundaries = [\
&emsp;&emsp;(max(0, s), min(total_samples, e))\
&emsp;&emsp;for s, e in boundaries\
        
GenAI helped us troubleshoot and understand how to run the code locally on our GPU by guiding us through installing CUDA and associated dependencies. Refer to the documentation we used for crepe and librosa below: 
1. https://github.com/marl/crepe
2. https://librosa.org/doc/latest/index.html

# Acknowledgements & External Sources

Claude 4.6 was used for assistance writing code for the following parts:
1. get_pitch() function - it helped write the code to convert stereo files to mono and to normalize them to 32 bit floats for use pitch detecting.\
2. to help write the logic to ensure our audio arrays didn't go out of bounds to make our code more robust: \
  total_samples = len(data)\
  boundaries = [\
&emsp;(max(0, s), min(total_samples, e))\
&emsp;for s, e in boundaries\
  ]
3. We also used Generative AI to help identify and troubleshoot syntax errors during development.

Code that allows user to open folders was made with code written by Reddit user socal_nerdtastic as reference.

## Setup and Usage

Given the use of Crepe for pitch detection, Python 3.13 is unsupported. Also, TensorFlow does not run on some cloud-based IDEs. For best results, a locall IDE with a supported GPU is recommended. For GPU acceleration, more 16+ GB of VRAM is reccomended.

To run this code, numpy, scipy, crepe, librosa, tkinter, and tensorflow are required. 

To use it, download and place all python files and the CONFIG file in a folder. Run the script note_cutout.py to cutout the notes. To choose where the input files are located and where to save the cutout files, the program will offer the user two file windows to choose their input and output folders. Due to the machine leaning, the cutout process might take time depending on the hardware used.

To use GPU acceleration to speed up the machine learning, in the CONFIG file, set the GPU acceleraion setting to "Y".





