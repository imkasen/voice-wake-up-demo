"""
Official Code Demo 2
"""

from pocketsphinx import LiveSpeech

if __name__ == "__main__":
    speech = LiveSpeech(keyphrase="hello", kws_threshold=1e-20)

    for phrase in speech:
        print(phrase.segments(detailed=True))
