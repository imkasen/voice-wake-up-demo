"""
Vosk Official Test Demo
"""

import json
import os
import sys
import wave

from pyaudio import PyAudio, paInt16
from vosk import KaldiRecognizer, Model, SetLogLevel


def empty(_model: Model):
    """
    test_empty.py
    """
    rec = KaldiRecognizer(_model, 16000)

    print(json.loads(rec.FinalResult()))


def simple(_model: Model, _wf: wave.Wave_read):
    """
    test_simple.py
    """

    rec = KaldiRecognizer(_model, _wf.getframerate())  # 创建 Recognizer 对象
    rec.SetWords(True)  # KaldiRecognizer 的 Result() 和 FinalResult() 方法将在其 JSON 输出中包含识别的单词及其时间戳。
    rec.SetPartialWords(True)  # KaldiRecognizer 的 PartialResult() 方法将在其 JSON 输出中包含识别的单词及其时间戳。

    # """
    # 如果 AcceptWaveform() 方法返回 True，
    # 表明语音识别过程已经找到了一个或多个稳定的词语（比如，话语的间隙或者片段的终点），
    # 并且可以通过 Result() 方法获取完整的识别结果（返回识别的语句，可能包含了多个词语）。

    # 如果 AcceptWaveform() 方法返回 False，
    # 表明语音识别过程还在继续，还没找到稳定的词语，
    # 可以通过 PartialResult() 方法获取部分识别结果（返回的只是当前识别的部分信息，可能只包含一个或者部分词语）。
    # """
    while True:
        data: bytes = _wf.readframes(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(f"Result: {json.loads(rec.Result())}")  # 识别结果
        else:
            print(f"PartialResult: {json.loads(rec.PartialResult())}")  # 部分识别结果

    # 这个方法在每次完成一段完整的音频处理（如一句话或一段对话）时调用，用于获取该段音频的完整识别结果。
    print(f"FinalResult: {json.loads(rec.FinalResult())}")


def text(_model: Model, _wf: wave.Wave_read):
    """
    test_text.py
    """
    rec = KaldiRecognizer(_model, _wf.getframerate())
    while True:
        data: bytes = _wf.readframes(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            print(f"Result: {res['text']}")

    res = json.loads(rec.FinalResult())
    print(f"FinalResult: {res['text']}")


def reset(_model: Model, _wf: wave.Wave_read):
    """
    test_reset.py
    """
    rec = KaldiRecognizer(_model, _wf.getframerate())
    while True:
        data: bytes = wf.readframes(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(f"Result: {json.loads(rec.Result())}")
            sys.exit(1)
        else:
            jres = json.loads(rec.PartialResult())
            print(jres)

            if jres["partial"] == "one zero zero zero":
                print("We can reset recognizer here and start over")
                # 重置识别器到初始状态。
                # 这意味着识别器会清除之前处理的所有音频数据和中间状态，就像刚刚创建一个新的识别器实例一样。
                # 使用 Reset() 方法可以在不创建新识别器的情况下开始新的一轮语音识别。
                rec.Reset()


def alternatives(_model: Model, _wf: wave.Wave_read):
    """
    test_alternatives.py
    """

    rec = KaldiRecognizer(_model, _wf.getframerate())
    # 设置识别结果的最大候选项数量
    # Result() 和 FinalResult() 方法将会返回 JSON 输出，包含最容易识别为正确结果的 10 个候选项。
    rec.SetMaxAlternatives(10)

    while True:
        data: bytes = _wf.readframes(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(f"Result: {json.loads(rec.Result())}")
        else:
            print(f"PartialResult: {json.loads(rec.PartialResult())}")

    print(f"FinalResult: {json.loads(rec.FinalResult())}")


def grammar(_model: Model, _wf: wave.Wave_read):
    """
    test_words.py
    """
    # You can also specify the possible word or phrase list as JSON list, the order doesn't have to be strict
    lst1: list[str] = ["oh one two three", "four five six", "seven eight nine zero", "[unk]"]
    lst2: list[str] = ["one zero one two three oh", "four five six", "seven eight nine zero", "[unk]"]

    rec = KaldiRecognizer(
        _model,
        _wf.getframerate(),
        json.dumps(lst1),
    )

    while True:
        data: bytes = wf.readframes(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(f"Result: {json.loads(rec.Result())}")
            # 用来改变或重设语法规则。
            rec.SetGrammar(json.dumps(lst2))
        else:
            print(f"PartialResult: {json.loads(rec.PartialResult())}")

    print(f"FinalResult: {json.loads(rec.FinalResult())}")


def microphone(_model: Model):
    """
    audio input from microphone
    """
    rec = KaldiRecognizer(_model, 16000)
    p = PyAudio()
    stream = p.open(format=paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    while True:
        data: bytes = stream.read(4096)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            print(f"Result: {json.loads(rec.Result())}")
        else:
            res = json.loads(rec.PartialResult())
            if res["partial"]:
                print(f"PartialResult: {res['partial']}")

    print(f"FinalResult: {json.loads(rec.FinalResult())}")


if __name__ == "__main__":
    # set log level to -1 to disable debug messages
    SetLogLevel(level=-1)

    dir_path: str = os.path.dirname(os.path.abspath(__file__))
    en_model_path: str = os.path.join(dir_path, "vosk-model-small-en-us-0.15")
    cn_model_path: str = os.path.join(dir_path, "vosk-model-small-cn-0.22")

    wf: wave.Wave_read = wave.open(os.path.join(dir_path, "test.wav"), "rb")

    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Audio file must be WAV format mono PCM.")
        sys.exit(1)

    # init model by name or with a folder path
    # vosk_model = Model(lang="en-us")
    # model = Model(model_path=en_model_path)
    model = Model(model_path=cn_model_path)

    # empty(model)
    # simple(model, wf)
    # text(model, wf)
    # reset(model, wf)
    # alternatives(model, wf)
    # grammar(model, wf)
    microphone(model)
