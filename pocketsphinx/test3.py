"""
Official Code Demo 3

RuntimeError: Failed to initialize PocketSphinx
"""

from pocketsphinx import LiveSpeech, get_model_path

if __name__ == "__main__":
    speech = LiveSpeech(
        hmm=get_model_path("en-us"),
        lm=get_model_path("en-us.lm.bin"),
        dic=get_model_path("cmudict-en-us.dict"),
    )

    for phrase in speech:
        print(phrase)
