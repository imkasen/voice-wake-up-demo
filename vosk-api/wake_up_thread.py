"""
Voice Wake Up Demo
"""

import difflib
import json
import os
import queue
import threading
import time

import noisereduce as nr
import numpy as np
import pyaudio
import webrtcvad
from vosk import KaldiRecognizer, Model, SetLogLevel


class VoiceDetector:
    """
    Detect voice
    """

    def __init__(self, _model: Model, word: str) -> None:
        self.model: Model = _model
        self.word: str = word
        self.vad = webrtcvad.Vad(mode=1)
        self.sample_rate = 16000
        self.vad_duration_ms = 30  # ms
        self.frame_size = int(self.sample_rate * self.vad_duration_ms / 1000)

        self.audio_queue = queue.Queue(maxsize=1024)
        self.stop_event = threading.Event()

    def words_compare(self, word1: str, word2: str, threshold: float = 0.8) -> bool:
        """
        compare keyword and asr result
        """

        def word_process(word: str) -> str:
            return word.replace(" ", "").lower()

        similarity_score: float = difflib.SequenceMatcher(None, word_process(word1), word_process(word2)).ratio()
        print(f"Similarity score: {similarity_score}")

        return similarity_score >= threshold

    def noise_reduce(self, data_bytes: bytes, sr: int) -> bytes:
        """
        noise reduce
        """
        data_ndarray = np.frombuffer(buffer=data_bytes, dtype=np.int16)
        reduced_data = nr.reduce_noise(y=data_ndarray, sr=sr)
        return reduced_data.tobytes()

    def audio_capture(self):
        """
        capture audio data from pyaudio
        """
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.frame_size,
            )
            stream.start_stream()
            print("Start audio capture from microphone...")

            while (not self.stop_event.is_set()) and stream.is_active():
                print("read data from pyaudio stream.")

                frame: bytes = stream.read(self.frame_size)
                self.audio_queue.put(frame)

        except OSError as e:
            print(f"An I/O error occurred during audio capture: {e}")
        finally:
            print("End audio capture...")
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.stop_event.set()

    def audio_process(self):
        """
        process audio using webrtcvad, vosk
        """
        try:
            rec = KaldiRecognizer(self.model, self.sample_rate)
            empty_queue_printed = False

            while not self.stop_event.is_set():
                if not self.audio_queue.empty():
                    print("get data from audio queue.")
                    empty_queue_printed = False

                    frame: bytes = self.audio_queue.get()
                    if self.vad.is_speech(frame, self.sample_rate):
                        # data = noise_reduce(data, sample_rate)  # slow
                        if rec.AcceptWaveform(frame):
                            res_text: str = json.loads(rec.Result())["text"]
                        else:
                            res_text: str = json.loads(rec.PartialResult())["partial"]
                        if res_text:
                            print(res_text)
                            rec.Reset()
                            if self.words_compare(res_text, self.word):
                                print(f"Detect '{res_text}'!")
                                self.stop_event.set()
                                break
                else:
                    if not empty_queue_printed:
                        print("audio queue is empty, wait...")
                        empty_queue_printed = True

        except OSError as e:
            print(f"An I/O error occurred during voice processing: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error during voice processing: {e}")
        finally:
            print("End audio processing...")
            self.stop_event.set()

    def start(self):
        """
        start
        """
        try:
            capture_thread = threading.Thread(target=self.audio_capture)
            process_thread = threading.Thread(target=self.audio_process)

            capture_thread.start()
            process_thread.start()

            return capture_thread, process_thread
        except RuntimeError as e:
            print(f"An error occurred during thread initialization: {e}")
            self.stop_event.set()
            return None, None


if __name__ == "__main__":
    SetLogLevel(-1)

    dir_path: str = os.path.dirname(os.path.abspath(__file__))
    en_model_path: str = os.path.join(dir_path, "vosk-model-small-en-us-0.15")
    cn_model_path: str = os.path.join(dir_path, "vosk-model-small-cn-0.22")

    model = Model(model_path=cn_model_path)
    # model = Model(model_path=en_model_path)

    EN_WORD = "jarvis"
    CN_WORD = "小白"

    vd = VoiceDetector(model, CN_WORD)
    ct, pt = vd.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Terminating: KeyboardInterrupt")
        vd.stop_event.set()
        if ct is not None:
            ct.join()
        if pt is not None:
            pt.join()
        print("Threads successfully terminated.")
