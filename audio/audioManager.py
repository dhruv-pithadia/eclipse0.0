import pyaudio
import webrtcvad
import queue
import logging

logger = logging.getLogger(__name__)

class AudioManager:
    def __init__(self, rate=16000, chunkDurationMs=30, bufferDurationMs=1000):
        self.rate = rate
        self.chunkSize = int(rate * chunkDurationMs / 1000)
        self.bufferSize = int(rate * bufferDurationMs / 1000)
        self.audioInterface = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(2)  # 0: Normal, 3: Most aggressive
        self.audioQueue = queue.Queue()

        logger.info("AudioManager initialized with rate %d Hz and chunk size %d.", self.rate, self.chunkSize)

    def startStream(self):
        try:
            self.audioStream = self.audioInterface.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunkSize
            )
            logger.info("Audio stream started.")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")

    def readAudio(self):
        try:
            audioData = self.audioStream.read(self.chunkSize, exception_on_overflow=False)
            return audioData
        except Exception as e:
            logger.error(f"Error reading audio data: {e}")
            return None

    def isSpeech(self, audioData):
        try:
            isSpeech = self.vad.is_speech(audioData, self.rate)
            logger.debug("isSpeech: %s", isSpeech)
            return isSpeech
        except Exception as e:
            logger.error(f"Error detecting speech: {e}")
            return False

    def stopStream(self):
        try:
            if self.audioStream:
                self.audioStream.stop_stream()
                self.audioStream.close()
                logger.info("Audio stream stopped.")
        except Exception as e:
            logger.error(f"Error stopping audio stream: {e}")