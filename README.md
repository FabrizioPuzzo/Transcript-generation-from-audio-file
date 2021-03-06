# Transcript generation from audio file

---

**Generating a transcript from an audio file with the Google Cloud Speech-to-Text API**

In this Python project the [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text) is used to generate a transcript from an audio file. 

---

# Files inculded

This project includes the following files:
* <code>main_demo.py</code> - main script
* <code>transcript_generator.py</code> - class for transcript generation

The folder 'audio_raw/' contains audio files that can be used to test the code (see 'Usage - Run demo'). This folder also contains the true transcripts of the provided audio files.

# Requirements

Python-Version: 3.7

All python packages needed to run the code are included in the 'requirements.txt' file. Read the section 'Usage - Run demo' on how to set up the python environment and on how to run the demo.

# Usage

### Setting up he python environment 

1. Download this repository. 
2. Create a virtual environment with Python 3.

    ```
    virtualenv -p python3 env1
    ```

3. Activate the environment.

    ```
    source env1/bin/activate
    ```

4. Install the required dependencies.

    ```
    pip3 install -r requirements.txt
    ```

### Run demo

1. Set parameters in <code>main_demo.py</code> (line 5 to 7).

2. Set location for your Google credentials JSON-file in <code>main_demo.py</code> (line 11).
    - How to get the Google credentials JSON-file: [click here](https://cloud.google.com/docs/authentication/getting-started)

3. Copy the audio files (.mp3 or .wav) into the folder 'audio_raw/'.

4. Run <code>main_demo.py</code>. The generated transcripts are stored in the folder 'transcripts/' (folder will be created automatically).

# References

* [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text)
