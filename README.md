# captioner
A simple script for creating caption files for Kohya from Disco Diffusion settings files and metadata.

The script first checks for the existence of "random_prompt" metadata chunk, and if found, uses that for the prompt.
Otherwise it uses the prompt lifted from the batch settings file.

The location for the images has to be set in the code by hand, default is './images'.
