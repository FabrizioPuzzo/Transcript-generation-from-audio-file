import io, os 
import shutil
import numpy as np

import pathlib
import scipy

import soundfile
import noisereduce as nr
from pydub import AudioSegment

from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums


class TranscriptGenerator():

	def __init__(self, language_code='de', max_len_snip_sec=50, 
		audio_encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16):

		self.language_code = language_code		# languge code ("en", "de"), see: https://cloud.google.com/speech-to-text/docs	
		self.max_len_snip = max_len_snip_sec	# length of audio snippets in sec - max 60 sec
		self.sample_rate_hertz = None 			# sample rate of audio file in hertz
		self.audio_encoding = audio_encoding	# Audio encoding 

		# correct snippet length
		if self.max_len_snip > 55:
			print('max_len_snip_sec was set to ' + \
				 str(max_len_snip_sec) + '- to big - max = 55 s \n' + \
				'- set to 55 s')
			self.max_len_snip = 55

	def _create_dir(self, dirname, clear_dir=False):
		try:
			os.mkdir(dirname)
		except:
			print("Folder " + dirname + " already exists")
			if clear_dir:
				for filename in os.listdir(dirname):
					file_path = os.path.join(dirname, filename)
					try:
						if os.path.isfile(file_path) or os.path.islink(file_path):
							os.unlink(file_path)
						elif os.path.isdir(file_path):
							shutil.rmtree(file_path)
					except Exception as e:
						print('Failed to delete %s. Reason: %s' % (file_path, e))

	def _extend_filename(self, filename, ending, keep_ext=False):
		tmp = filename.split('.')
		if keep_ext:
			filename_new = tmp[0] + '_' + ending + '.' + tmp[1]
		else:
			filename_new = tmp[0] + ending
		return filename_new

	def _convert_mp3_to_wav(self, path_audio):
		"""
		Converts .mp3 audio file to a .wav audio file. 
		Returns path to converted auido file.

		Args:
		path_audio: path of audio file
		"""

		path_audio_wav = self._extend_filename(path_audio, '.wav', False) 
		sound = AudioSegment.from_mp3(path_audio)
		sound.export(path_audio_wav, format="wav")
		return path_audio_wav

	def _convert_to_mono(self, path_audio):
		"""
		Converts stereo .wav audio file to a mono .wav audio file. 
		Returns path to converted auido file.

		Args:
		path_audio: path of audio file
		"""

		path_audio_mono = self._extend_filename(path_audio, 'mono', True)
		sound = AudioSegment.from_wav(path_audio)
		sound = sound.set_channels(1)
		sound.export(path_audio_mono, format="wav")
		return path_audio_mono

	def _convert_to_16Bit(self, path_audio):
		"""
		Converts .wav audio file to a .wav audio file with 16 Bit bit-depth. 
		Returns path to converted auido file.

		Args:
		path_audio: path of audio file
		"""

		path_audio_16Bit = self._extend_filename(path_audio, '16Bit', True)
		data, rate = soundfile.read(path_audio)
		soundfile.write(path_audio_16Bit, data, rate, subtype='PCM_16')
		return path_audio_16Bit

	def _filter_audio_nr(self, path_audio):
		"""
		Applies filter to given audio file. 
		Returns path to filtered auido file.
		Source code: https://timsainburg.com/noise-reduction-python.html

		Args:
		path_audio: path of audio file
		"""

		# Create path
		path_audio_filt = self._extend_filename(path_audio, 'filt', True)

		# load data
		rate, data = scipy.io.wavfile.read(path_audio)
		data = data / 32768

		# perform noise reduction
		data_reduced_noise = nr.reduce_noise(audio_clip=data, noise_clip=data, verbose=False)

		# save flitered audio
		scipy.io.wavfile.write(path_audio_filt, rate, data_reduced_noise)
		return path_audio_filt

	def _split_audio(self, path_audio):
		"""
		Splits audio file into 50 sec snippets. 
		Returns path to directory that contains the snippets.

		Args:
		path_audio: path of audio file
		"""

		# Create and empty folder
		dirname = os.path.join(os.path.dirname(__file__), 'snippets/')
		self._create_dir(dirname, True)

		# len() and slicing are in milliseconds
		max_len = self.max_len_snip * 1000
		start_point = -max_len 
		end_point = 0
		incr = -1
		done = False

		# slice soundfile
		sound = AudioSegment.from_wav(path_audio)
		while not done:
			# increment start- and endpoint
			incr += 1
			start_point += max_len
			end_point += max_len
			if end_point >= len(sound):
				done = True
				end_point = len(sound)

			# Create filename
			filename = os.path.join(os.path.dirname(__file__), \
				'snippets/part_' + str(incr).zfill(5) + '.wav')

			# Slice soundfile
			snippet = sound[start_point: end_point]
			snippet.export(filename, format="wav")

		return dirname

	def _audio_to_str_gc(self, path_audio):
		"""
		Performs synchronous speech recognition on an audio file

		Args:
		storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
		"""

		# Create client
		client = speech_v1p1beta1.SpeechClient()

		# The language of the supplied audio
		language_code = self.language_code

		# Sample rate in Hertz of the audio data sent
		sample_rate_hertz = self.sample_rate_hertz

		# Encoding of audio data sent. This sample sets this explicitly.
		# This field is optional for FLAC and WAV audio formats.
		encoding = self.audio_encoding
		config = {
			"language_code": language_code,
			"sample_rate_hertz": sample_rate_hertz,
			"encoding": encoding,
			}
		
		# Read audio file
		with io.open(path_audio, "rb") as f:
			content = f.read()
		audio = {"content": content}

		# Process audio file
		response = client.recognize(config, audio)

		# Put together text string
		text = ''
		for result in response.results:
			# First alternative is the most probable result
			alternative = result.alternatives[0]
			#print(u"Transcript: {}".format(alternative.transcript))
			text += alternative.transcript

		return text
	
	def _preprocess_audio(self, path_audio, apply_filter=False):
		"""
		Performs the following preprocessing steps: 'convert to .wav', 'convert from stereo to mono',
		'apply filter', 'convert to 16 Bit bit-depth '. Returns path to preprocessed audio file.

		Args:
		path_audio: path of original (raw) audio file
		apply_filter: bool to determine if a filter should be applied. 
					  Note: The Google Cloud Speech-to-Text API applies a filter of it's own.
		"""

		# Convert to wav
		if path_audio.endswith('.mp3'):
			path_audio = self._convert_mp3_to_wav(path_audio)

		# Convert stereo to mono
		path_audio = self._convert_to_mono(path_audio)

		# Apply filter
		if apply_filter:
			# Filter audio file
			path_audio = self._filter_audio_nr(path_audio)	

		# Convert to 16 bit
		path_audio = self._convert_to_16Bit(path_audio)

		return path_audio

	def generate_transcript(self, path_audio_orig, apply_filter=False):
		"""
		Generates transcript from an audio file. The audio files is 
		first preprocessed and splitt into 50 second snippets. The splitting 
		is necessary because the implemented method of the 
		Google Cloud Speech-to-Text API accepts only audio files with a 
		maximum lenght up to 60 seconds. To implement the method to process longer audio files,
		the audio files must be stored in a google cloud bucket. 
		See: https://cloud.google.com/speech-to-text/docs/async-recognize

		Args:
		path_audio_orig: path of original (raw) audio file
		apply_filter: bool to determine if a filter should be applied. 
					  Note: The Google Cloud Speech-to-Text API applies a filter of it's own.
		"""

		# Create paths
		dir_audio_prepro = os.path.join(os.path.dirname(__file__), 'audio_prepro/')
		self._create_dir(dir_audio_prepro, False)
		path_audio = shutil.copy(path_audio_orig, dir_audio_prepro)

		dir_trans = os.path.join(os.path.dirname(__file__), 'transcripts/')
		self._create_dir(dir_trans, False)
		tmp = path_audio_orig.split('/')[-1]
		path_trans = os.path.join(dir_trans, 
				'transcript_' + tmp.split('.')[0] + '.txt')
		if apply_filter:
			path_trans = self._extend_filename(path_trans, '_filt', True)

		# Preprocess audio file
		path_audio = self._preprocess_audio(path_audio, apply_filter)

		# Get sample rate
		rate, data = scipy.io.wavfile.read(path_audio)
		self.sample_rate_hertz = rate

		# split audio file
		dir_snip = self._split_audio(path_audio)	

		num_snip = []
		str_snip = []
		for snip in os.listdir(dir_snip):
			if snip.endswith(".mp3") or snip.endswith(".wav"):
				# getting numbers from string  
				data = snip.split("_")
				data = data[1].split(".")
				num = int(data[0])
				#print(num)
				num_snip.append(num)
				str_snip.append(\
					self._audio_to_str_gc(\
					os.path.join(dir_snip, snip)))

		num_snip_sort = np.argsort(num_snip)
		str_snip_sort = []

		for i in range(len(str_snip)):
			str_snip_sort.append(str_snip[num_snip_sort[i]])

		# put string together
		print(str_snip_sort)
		str_trans = ''
		for s in str_snip_sort:
			str_trans += s + ' | '

		# write to textfile
		text_file = open(path_trans, "w")
		text_file.write(str_trans)
		text_file.close()










