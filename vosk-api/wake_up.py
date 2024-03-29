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
    print("Noise reduced...")
    return reduced_data.tobytes()


def wake_up(_model: Model, word: str):
    """
    voice wake up based on the audio input from microphone
    """
    sample_rate = 16000
    vad_duration_ms = 30
    frames_num = int(sample_rate * vad_duration_ms / 1000)

    # vad = webrtcvad.Vad()
    # vad.set_mode(1)  # [0, 3]

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
            data: bytes = stream.read(frames_num, exception_on_overflow=False)

            # if vad.is_speech(data, sample_rate):  # VAD
            #     print("Voice detected...")

            data = noise_reduce(data, sample_rate)

            if rec.AcceptWaveform(data):
                res_text = json.loads(rec.Result())["text"]
                if res_text:
                    print(res_text)
            else:
                res_text: str = json.loads(rec.PartialResult())["partial"]
                if res_text:
                    print(res_text)
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
    frames_num = 4096

    rec = KaldiRecognizer(_model, sample_rate)

    def callback(in_data, frame_count, time_info, status):  # pylint: disable=W0613
        # TODO

        data: bytes = noise_reduce(in_data, sample_rate)

        if rec.AcceptWaveform(data):
            res_text = json.loads(rec.Result())["text"]
            if res_text:
                print(res_text)
        else:
            res_text = json.loads(rec.PartialResult())["partial"]
            if res_text:
                print(res_text)
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

    wake_up(model, CN_WORD)
    # wake_up_callback(model, CN_WORD)
