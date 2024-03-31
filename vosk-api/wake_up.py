"""
Voice Wake Up Demo
"""

import difflib
import json
import os

import noisereduce as nr
import numpy as np
import pyaudio
import webrtcvad
from vosk import KaldiRecognizer, Model, SetLogLevel


def words_compare(word1: str, word2: str, threshold: float = 0.8) -> bool:
    """
    compare keyword and asr result
    """

    def word_process(word: str) -> str:
        return word.replace(" ", "").lower()

    similarity_score: float = difflib.SequenceMatcher(None, word_process(word1), word_process(word2)).ratio()
    print(f"Similarity score: {similarity_score}")

    return similarity_score >= threshold


def noise_reduce(data_bytes: bytes, sr: int) -> bytes:
    """
    noise reduce
    """
    data_ndarray = np.frombuffer(buffer=data_bytes, dtype=np.int16)
    reduced_data = nr.reduce_noise(y=data_ndarray, sr=sr)
    return reduced_data.tobytes()


def wake_up(_model: Model, word: str):
    """
    voice wake up based on the audio input from microphone
    """
    sample_rate = 16000
    vad_duration_ms = 30
    frame_duration_sec: float = vad_duration_ms / 1000
    frame_size = int(sample_rate * frame_duration_sec)

    vad = webrtcvad.Vad()
    vad.set_mode(1)  # [0, 3]

    rec = KaldiRecognizer(_model, sample_rate)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_size,
    )
    stream.start_stream()
    print("Start...")

    try:
        while stream.is_active():
            data: bytes = stream.read(frame_size, exception_on_overflow=False)
            if vad.is_speech(data, sample_rate):
                # data = noise_reduce(data, sample_rate)  # slow
                if rec.AcceptWaveform(data):
                    res_text: str = json.loads(rec.Result())["text"]
                else:
                    res_text: str = json.loads(rec.PartialResult())["partial"]
                if res_text:
                    print(res_text)
                    rec.Reset()
                    if words_compare(res_text, word):
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
    vad_duration_ms = 30
    frame_duration_sec: float = vad_duration_ms / 1000
    frame_size = int(sample_rate * frame_duration_sec)

    rec = KaldiRecognizer(_model, sample_rate)

    vad = webrtcvad.Vad()
    vad.set_mode(1)  # [0, 3]

    def callback(in_data, frame_count, time_info, status):  # pylint: disable=W0613
        if vad.is_speech(in_data, sample_rate):
            if rec.AcceptWaveform(in_data):
                res_text = json.loads(rec.Result())["text"]
            else:
                res_text = json.loads(rec.PartialResult())["partial"]
            if res_text:
                print(res_text)
                rec.Reset()
                if words_compare(res_text, word):
                    print(f"Detect '{res_text}'!")
                    return (None, pyaudio.paComplete)
        return (in_data, pyaudio.paContinue)

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_size,
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

    wake_up(model, CN_WORD)
    # wake_up_callback(model, CN_WORD)
