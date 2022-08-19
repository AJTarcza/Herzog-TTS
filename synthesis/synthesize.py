import os
import torch
import numpy as np
from scipy.io.wavfile import write
from os.path import dirname, abspath
import sys
import time

import nltk

nltk.download("punkt")

sys.path.append(dirname(dirname(abspath(__file__))))

from training.tacotron2_model import Tacotron2
from training.clean_text import clean_text
from training import DEFAULT_ALPHABET
from synthesis.vocoders import Hifigan

def load_model(model_path):
    """
    Loads the Tacotron2 model.
    Uses GPU if available, otherwise uses CPU.

    Parameters
    ----------
    model_path : str
        Path to tacotron2 model

    Returns
    -------
    Tacotron2
        Loaded tacotron2 model
    """
    if torch.cuda.is_available():
        model = Tacotron2().cuda()
        model.load_state_dict(torch.load(model_path)["state_dict"])
        _ = model.cuda().eval().half()
    else:
        model = Tacotron2()
        model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu"))["state_dict"])
    return model


def text_to_sequence(text, symbols):
    """
    Generates text sequence for audio file

    Parameters
    ----------
    text : str
        Text to synthesize
    symbols : list
        List of valid symbols
    """
    symbol_to_id = {s: i for i, s in enumerate(symbols)}
    sequence = np.array([[symbol_to_id[s] for s in text if s in symbol_to_id]])
    if torch.cuda.is_available():
        return torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()
    else:
        return torch.autograd.Variable(torch.from_numpy(sequence)).cpu().long()


def synthesize(
    model,
    text,
    symbols=DEFAULT_ALPHABET,
    audio_path=None,
    vocoder=None,
    silence_padding=0.15,
    sample_rate=22050,
    max_decoder_steps=3000,
    split_text=False,
):
    """
    Synthesise text for a given model.
    Produces graph and/or audio file when given.
    Supports multi line synthesis (seperated by \n).

    Parameters
    ----------
    model : Tacotron2
        Tacotron2 model
    text : str/list
        Text to synthesize (or list of lines to synthesize)
    symbols : list
        List of symbols (default is English)
    audio_path : str (optional)
        Path to save audio file to
    vocoder : Object (optional)
        Vocoder model (required if generating audio)
    silence_padding : float (optional)
        Seconds of silence to seperate each clip by with multi-line synthesis (default is 0.15)
    sample_rate : int (optional)
        Audio sample rate (default is 22050)
    max_decoder_steps : int (optional)
        Max decoder steps controls sequence length and memory usage during inference.
        Increasing this will use more memory but may allow for longer sentences. (default is 1000)
    split_text : bool (optional)
        Whether to use the split text tool to convert a block of text into multiple shorter sentences
        to synthesize (default is True)

    Raises
    -------
    AssertionError
        If audio_path is given without a vocoder
    """
    print("Synthesizing audio...")
    
    start_time = time.time()
 
    if audio_path:
        assert vocoder, "Missing vocoder"

    if not isinstance(text, list) and split_text:
        # Split text into multiple lines
        text = nltk.tokenize.sent_tokenize(text)

    if isinstance(text, list):
        # Multi-lines given
        text = [line.strip() for line in text if line.strip()]
        mels = []
        alignments = []
        for line in text:
            text = clean_text(line, symbols)
            sequence = text_to_sequence(text, symbols)
            _, mel_outputs_postnet, _, alignment = model.inference(sequence, max_decoder_steps)
            mels.append(mel_outputs_postnet)
            alignments.append(alignment)

        if audio_path:
            silence = np.zeros(int(silence_padding * sample_rate)).astype("int16")
            audio_segments = []
            for i in range(len(mels)):
                audio_segments.append(vocoder.generate_audio(mels[i]))
                if i != len(mels) - 1:
                    audio_segments.append(silence)

            audio = np.concatenate(audio_segments)
            write(audio_path, sample_rate, audio)
    else:
        # Single sentence
        text = clean_text(text.strip(), symbols)
        sequence = text_to_sequence(text, symbols)
        _, mel_outputs_postnet, _, alignment = model.inference(sequence, max_decoder_steps)

        if audio_path:
            audio = vocoder.generate_audio(mel_outputs_postnet)
            write(audio_path, sample_rate, audio)
            
    end_time = time.time()
    
    print("Synthesis completed in %s second(s)" % (end_time - start_time))

