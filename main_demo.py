import pathlib
import os, sys
from transcript_generator import TransscriptGenerator

LANGUAGE_CODE = 'de'		# languge code ("en", "de"), see: https://cloud.google.com/speech-to-text/docs							
APPLY_FILTER = False		# Apply an implemented filter - not needed in most cases - Google Cloud API Speech-to-text applies own filter
DIR_AUDIO_FIlES = os.path.join(os.path.dirname(__file__), 'audio_raw') # directory that contains the raw audio files


# Set credentials for google api
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 

# Create object
transGen = TransscriptGenerator(LANGUAGE_CODE)

# Iterate through directory
for filename_audio in os.listdir(DIR_AUDIO_FIlES):
	if filename_audio.endswith(".mp3") or filename_audio.endswith(".wav"):

		# Create path to audio file
		path_audio = os.path.join(DIR_AUDIO_FIlES, filename_audio)

 		# Generate transcript
		transGen.generate_transcript(path_audio, APPLY_FILTER)