import simpleaudio as audio

elegantWav = audio.WaveObject.from_wave_file(r"res\elegant.wav")
pristineWav = audio.WaveObject.from_wave_file(r"res\pristine.wav")

def audio_ping():
    elegantWav.play()

def chime():
    pristineWav.play()


