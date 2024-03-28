"""
Voice Wake Up Demo
"""

import json
import os

import pyaudio
from vosk import KaldiRecognizer, Model, SetLogLevel


def wake_up(_model: Model, word: str):
    """
    voice wake up based on the audio input from microphone
    """
    sample_rate = 16000
    frames_num = 4096

    rec = KaldiRecognizer(_model, sample_rate)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frames_num,
    )
    stream.start_stream()
    print("Start...")

    try:
        while stream.is_active():
            data: bytes = stream.read(frames_num)
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                print(res["text"])
            else:
                res_text: str = json.loads(rec.PartialResult())["partial"]
                if res_text:
                    print(res_text)
                    if word in res_text.lower():
                        print(f"Detect '{res_text}'!")
                        break
    except KeyboardInterrupt:
        print("KeyboardInterrupt...")
    finally:
        print("End...")
        stream.stop_stream()
        stream.close()
        p.terminate()


def wake_up_callback(_model: Model, word: str):
    """
    voice wake up based on the audio input from microphone, using pyaudio callback
    """
    sample_rate = 16000
    frames_num = 4096

    rec = KaldiRecognizer(_model, sample_rate)

    def callback(in_data, frame_count, time_info, status):  # pylint: disable=W0613
        if rec.AcceptWaveform(in_data):
            res = json.loads(rec.Result())
            print(res["text"])
        else:
            res_text = json.loads(rec.PartialResult())["partial"]
            if res_text:
                print(res_text)
                if word in res_text.lower():
                    print(f"Detect '{res_text}'!")
                    return (None, pyaudio.paComplete)
        return (in_data, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frames_num,
        stream_callback=callback,
    )

    print("Start...")
    stream.start_stream()

    try:
        while stream.is_active():
            pass
    except KeyboardInterrupt:
        print("KeyboardInterrupt...")
    finally:
        print("End...")
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    SetLogLevel(-1)

    dir_path: str = os.path.dirname(os.path.abspath(__file__))
    en_model_path: str = os.path.join(dir_path, "vosk-model-small-en-us-0.15")
    cn_model_path: str = os.path.join(dir_path, "vosk-model-small-cn-0.22")

    model = Model(model_path=cn_model_path)
    # model = Model(model_path=en_model_path)

    EN_WORD = "jarvis"
    CN_WORD = "小白"

    # wake_up(model, CN_WORD)
    wake_up_callback(model, CN_WORD)
