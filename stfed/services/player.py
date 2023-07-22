import wave
import io

import simpleaudio


wave_obj = None
f = None

def start(content: bytes):
    global f
    global wave_obj
    stop()
    f = io.BytesIO(content)
    wave_read = wave.open(f)
    wave_obj = simpleaudio.WaveObject.from_wave_read(wave_read)
    wave_obj = wave_obj.play()

def stop():
    global wave_obj
    global f
    if wave_obj is None:
        return
    wave_obj.stop()
    wave_obj = None
    f.close()
    f = None
