import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io

def get_audio_bytes(text):
    # This converts text to speech and returns the audio binary
    tts = gTTS(text=text, lang='en', tld='co.uk')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.read()
