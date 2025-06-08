import sys
import os
import tempfile
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
import sounddevice as sd
import numpy as np
import wave
import pygame
from pygame import mixer
from googletrans import Translator
import speech_recognition as sr
from gtts import gTTS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='translator.log'
)

# Set temp directory explicitly for Ubuntu/WSL
tempfile.tempdir = '/tmp'

# Window configuration
Window.minimum_width = 300
Window.minimum_height = 500

class TranslatorApp(BoxLayout):
    status_text = StringProperty("Ready")
    status_color = ListProperty([0.1, 0.5, 0.2, 1])
    recording = BooleanProperty(False)
    
    languages = {
        "English": "en",
        "Spanish": "es",
        "Italian": "it",
        "French": "fr",
        "German": "de",
        "Chinese": "zh-CN",
        "Japanese": "ja",
        "Russian": "ru",
        "Arabic": "ar",
        "Igbo": "ig",
        "Yoruba": "yo",
        "Hausa": "ha"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.frames = []
        self.sample_rate = 44100
        self.audio_stream = None
        self.current_audio_file = None
        
        # Initialize audio systems with error handling
        try:
            # Print available audio devices
            logging.info("Available audio devices: %s", sd.query_devices())
            sd.default.device = 'default'
            
            # Initialize pygame mixer with Ubuntu-compatible settings
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=1)
            pygame.mixer.init()
            
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.translator = Translator()
            
            # Window configuration
            Window.size = (360, 640)
            Window.minimum_width = 360
            Window.minimum_height = 640
            Window.bind(on_request_close=self.prevent_close)
            
        except Exception as e:
            logging.error("Initialization error: %s", str(e))
            self.status_text = f"Init Error: {str(e)}"
            self.status_color = [0.8, 0.2, 0.2, 1]

    def prevent_close(self, *args):
        if self.recording:
            return True
        return False

    def set_status(self, message, success=True):
        self.status_text = message
        self.status_color = [0.1, 0.5, 0.2, 1] if success else [0.8, 0.2, 0.2, 1]

    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        try:
            self.recording = True
            self.frames = []
            self.audio_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32',
                callback=self.audio_callback
            )
            self.audio_stream.start()
            self.set_status("Recording...", success=True)
        except Exception as e:
            logging.error("Recording error: %s", str(e))
            self.set_status(f"Record error: {str(e)}", success=False)
            self.recording = False

    def stop_recording(self):
        if self.audio_stream:
            self.recording = False
            self.audio_stream.stop()
            self.audio_stream.close()
            self.set_status("Processing audio...", success=True)
            self.process_audio()

    def audio_callback(self, indata, frames, time, status):
        self.frames.append(indata.copy())

    def process_audio(self):
        if not self.frames:
            self.set_status("No audio recorded", success=False)
            return
            
        try:
            audio_data = np.concatenate(self.frames, axis=0)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmpfile:
                tmpfile_name = tmpfile.name
                with wave.open(tmpfile_name, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio_data * 32767).astype(np.int16))
                self.speech_to_text(tmpfile_name)
        except Exception as e:
            logging.error("Audio processing error: %s", str(e))
            self.set_status(f"Process error: {str(e)}", success=False)

    def speech_to_text(self, audio_file):
        try:
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                self.ids.input_text.text = text
                self.set_status("Audio processed", success=True)
        except sr.UnknownValueError:
            self.set_status("Could not understand audio", success=False)
        except sr.RequestError as e:
            self.set_status(f"Speech API error: {str(e)}", success=False)
        except Exception as e:
            logging.error("Speech recognition error: %s", str(e))
            self.set_status(f"Speech error: {str(e)}", success=False)
        finally:
            try:
                os.unlink(audio_file)
            except:
                pass

    def translate_text(self):
        try:
            text = self.ids.input_text.text.strip()
            if text:
                self.set_status("Translating...", success=True)
                src_lang = self.languages[self.ids.src_lang.text]
                dest_lang = self.languages[self.ids.dest_lang.text]
                translation = self.translator.translate(text, src=src_lang, dest=dest_lang)
                self.ids.output_text.text = translation.text
                self.set_status("Translation complete", success=True)
        except Exception as e:
            logging.error("Translation error: %s", str(e))
            self.set_status(f"Translation error: {str(e)}", success=False)

    def play_audio(self, text, lang_code):
        if not text:
            self.set_status("No text to speak", success=False)
            return

        try:
            if self.current_audio_file and os.path.exists(self.current_audio_file):
                try:
                    os.unlink(self.current_audio_file)
                except:
                    pass

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                self.current_audio_file = f.name
                tts = gTTS(text=text, lang=lang_code)
                tts.save(f.name)

            mixer.music.load(self.current_audio_file)
            mixer.music.play()
            self.set_status("Playing audio...", success=True)

            duration = mixer.Sound(self.current_audio_file).get_length()
            Clock.schedule_once(lambda dt: self.cleanup_audio(), duration + 0.5)

        except Exception as e:
            logging.error("Audio playback error: %s", str(e))
            self.set_status(f"Playback error: {str(e)}", success=False)

    def cleanup_audio(self):
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                os.unlink(self.current_audio_file)
                self.current_audio_file = None
            except:
                pass

    def play_source_audio(self):
        text = self.ids.input_text.text.strip()
        if text:
            self.play_audio(text, self.languages[self.ids.src_lang.text])

    def play_translated_audio(self):
        text = self.ids.output_text.text.strip()
        if text:
            self.play_audio(text, self.languages[self.ids.dest_lang.text])

    def clear_text(self):
        self.ids.input_text.text = ""
        self.ids.output_text.text = ""
        self.set_status("Ready", success=True)

class VoiceTranslatorApp(App):
    def build(self):
        Window.clearcolor = (0.75, 0.75, 0.75, 1)
        return TranslatorApp()

if __name__ == '__main__':
    try:
        VoiceTranslatorApp().run()
    except Exception as e:
        logging.critical("Application crash: %s", str(e))
        sys.exit(1)