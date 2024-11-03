import os
import pyaudio
import webrtcvad
from google.cloud import speech_v1 as speech
import logging
import queue

logger = logging.getLogger(__name__)

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ''

class AudioTranscriber:
    def __init__(self):
        logger.info("Initializing AudioTranscriber...")
        self.speechClient = speech.SpeechClient()

        # Audio recording parameters
        self.RATE = 16000
        self.CHUNK_DURATION_MS = 30  # 30 ms per frame
        self.CHUNK_SIZE = int(self.RATE * self.CHUNK_DURATION_MS / 1000)  # Number of samples per frame
        self.BUFFER_DURATION_MS = 1000  # Buffer for 1 second of audio
        self.BUFFER_SIZE = int(self.RATE * self.BUFFER_DURATION_MS / 1000)

        self.audioInterface = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(2)  # Mode for balanced VAD sensitivity

        self.audioQueue = queue.Queue()

        try:
            self.audioStream = self.audioInterface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE
            )
            logger.info("AudioTranscriber initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing audio stream: {e}")

    def isSpeech(self, audioData):
        try:
            isSpeech = self.vad.is_speech(audioData, self.RATE)
            logger.debug("isSpeech: %s", isSpeech)
            return isSpeech
        except Exception as e:
            logger.error(f"Error in VAD speech detection: {e}")
            return False

    def transcribeAudio(self, audioData):
        try:
            streamingConfig = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.RATE,
                    language_code="en-US"
                ),
                interim_results=False
            )
            requests = (speech.StreamingRecognizeRequest(audio_content=audioData),)
            responses = self.speechClient.streaming_recognize(streamingConfig, requests)
            logger.info("Transcription completed.")
            return responses
        except Exception as e:
            logger.error(f"An error occurred during transcription: {e}")
            return None

    def startStream(self):
        logger.info("Starting audio stream...")
        try:
            self.audioStream.start_stream()
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")

    def readAudio(self):
        try:
            audioData = self.audioStream.read(self.CHUNK_SIZE, exception_on_overflow=False)
            logger.debug("Audio data read from stream.")
            return audioData
        except Exception as e:
            logger.error(f"Error reading audio data: {e}")
            return None

    def stopStream(self):
        logger.info("Stopping audio stream...")
        try:
            if self.audioStream:
                self.audioStream.stop_stream()
                self.audioStream.close()
                logger.info("Audio stream stopped.")
        except Exception as e:
            logger.error(f"Error stopping audio stream: {e}")