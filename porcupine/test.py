"""
Pvporcupine Demo
"""

import os
import struct
import sys

import pvporcupine
import pyaudio
from dotenv import load_dotenv


def keywords():
    """
    print default keywords
    """
    print(f"Porcupine default keywords: {pvporcupine.KEYWORDS}")


def detect(handle: pvporcupine.Porcupine):
    """
    Detect keywords
    """

    print(f"Porcupine version: {handle.version}")
    print(f"Porcupine frame length: {handle.frame_length}")
    print(f"porcupine sample rate: {handle.sample_rate}")

    sample_rate: int = handle.sample_rate
    frame_size: int = handle.frame_length

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_size,
    )
    stream.start_stream()
    print("Start audio capture from microphone...")

    try:
        while stream.is_active():
            pcm: bytes = stream.read(frame_size)
            pcm = struct.unpack_from("h" * handle.frame_length, pcm)

            keyword_index: int = handle.process(pcm)
            if keyword_index == 0:
                print("Detect 'jarvis'...")
                break
            if keyword_index == 1:
                print("Detect 'bumblebee'...")
                break
            if keyword_index < 0:
                print("Nothing...")

    except KeyboardInterrupt:
        print("KeyboardInterrupt...")
    except pvporcupine.PorcupineError as e:
        print(f"A porcupine error occurred during audio capture: {e}")
    finally:
        print("End audio capture...")
        stream.stop_stream()
        stream.close()
        handle.delete()
        p.terminate()


if __name__ == "__main__":
    if os.path.isfile(".env"):
        load_dotenv()
        access_key: str = os.getenv("access_key")
    else:
        sys.exit("Please create '.env' with porcupine access_key.")

    default_porcupine = pvporcupine.create(
        access_key=access_key,
        keywords=["jarvis", "bumblebee"],  # default keywords
    )

    # porcupine = pvporcupine.create(
    #     access_key=access_key,
    #     keyword_paths=["path/to/non/default/keyword/file"],  # custom wake word file (.ppn)
    #     model_path="path/to/model/file",  # non-English wake word model file (.pv)
    # )

    keywords()
    detect(default_porcupine)
