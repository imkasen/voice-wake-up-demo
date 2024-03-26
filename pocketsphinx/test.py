"""
Official Code Demo 1
The accuracy is very low
"""

from pocketsphinx import LiveSpeech

if __name__ == "__main__":
    for phrase in LiveSpeech():
        print(phrase)
