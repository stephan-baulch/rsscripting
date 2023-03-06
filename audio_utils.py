import simpleaudio as audio

# bidoopWav = audio.WaveObject.from_wave_file(r"res\bidoop.wav")
# chirpWav = audio.WaveObject.from_wave_file(r"res\chirp.wav")
# harpWav = audio.WaveObject.from_wave_file(r"res\harp.wav")
# longpopWav = audio.WaveObject.from_wave_file(r"res\longpop.wav")
# popWav = audio.WaveObject.from_wave_file(r"res\pop.wav")

elegantWav = audio.WaveObject.from_wave_file(r"res\elegant.wav")
pristineWav = audio.WaveObject.from_wave_file(r"res\pristine.wav")

# def bidoop():
#     bidoopWav.play()
#
# def chirp():
#     chirpWav.play()
#
# def harp():
#     harpWav.play()
#
# def longpop():
#     longpopWav.play()
#
# def pop():
#     popWav.play()

def audio_ping():
    elegantWav.play()

def chime():
    pristineWav.play()

