from google.cloud import texttospeech

def textToSpeech(text):
    client = texttospeech.TextToSpeechClient()
    synthesisInput = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audioConfig = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16)

    response = client.synthesize_speech(input=synthesisInput, voice=voice, audio_config=audioConfig)
    return response.audio_content

def saveAudioToFile(audioContent, filename="outputAudio.wav"):
    with open(filename, "wb") as audioFile:
        audioFile.write(audioContent)
    print(f"Audio saved to {filename}")