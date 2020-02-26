import pathlib
import os, sys
from transcript_generator import TransscriptGenerator

LANGUAGE_CODE = 'de'
APPLY_FILTER = False	
DIR_AUDIO_FIlES = os.path.join(os.path.dirname(__file__), 'audio_raw')
#print(DIR_AUDIO_FIlES)

# Set credentials for google api
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 

# Create object
transGen = TransscriptGenerator(LANGUAGE_CODE)

for filename_audio in os.listdir(DIR_AUDIO_FIlES):
	if filename_audio.endswith(".mp3") or filename_audio.endswith(".wav"):
		# Parameters
		path_audio = os.path.join(DIR_AUDIO_FIlES, filename_audio)

		#transGen._split_audio(tmp)
		transGen.generate_transscript(path_audio, APPLY_FILTER)