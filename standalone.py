import os
import torch
import numpy as np
import readline
from scipy.io.wavfile import write
from os.path import dirname, abspath
import sys
from time import time
from string import punctuation as punct

import nltk

nltk.download("punkt")

sys.path.append(dirname(dirname(abspath(__file__))))

from training.tacotron2_model import Tacotron2
from training.clean_text import clean_text
from training import DEFAULT_ALPHABET
from synthesis.vocoders import Hifigan

# Paths
APP_PATH = os.path.dirname(os.path.realpath(__file__))
MODEL = os.path.join(APP_PATH, "Model", "Werner_Herzog", "Werner_Herzog")
VOCODER_MODEL = os.path.join(APP_PATH, "Vocoder", "Pretrained", "g_02500000")
VOCODER_CONFIG = os.path.join(APP_PATH, "Vocoder", "Pretrained", "config.json")
AUDIO_PATH = os.path.join(APP_PATH, "Audio")

EXIT_KEYWORD = "exit"

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
    
    start_time = time()
 
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
            
    end_time = time()
    
    print("Synthesis completed in %s second(s)\n" % (end_time - start_time))

def main():
    # Make sure the models exist
    assert os.path.isfile(MODEL), "Model not found"
    assert os.path.isfile(VOCODER_MODEL), "vocoder model not found"
    
    # Create the Audio directory if it doesn't already exist
    if(not os.path.isdir(AUDIO_PATH)):
        os.mkdir(AUDIO_PATH)

    global model
    global vocoder
    
    # Load the models
    model = load_model(MODEL)
    vocoder = Hifigan(VOCODER_MODEL, VOCODER_CONFIG)
    
    os.system('cls||clear')
    
    text = ""
    
    # Run until the user enters the exit command
    while(text.lower() != EXIT_KEYWORD):
        # Fetch input from stdin
        print("Enter text (or '%s' to exit program): " % (EXIT_KEYWORD), end = " ")
        text = input()
        
        # Don't synthesize if the user entered the exit command
        if(text.lower() != EXIT_KEYWORD):
            # If the text didn't end with punctuation then just add a period
            if(text[-1] not in punct):
                text += '.'
            
            # Audio file path and name
            audio_file = AUDIO_PATH + "/%s.wav" % (time() * 1000)
            
            # Run the synthesizer
            try:
                synthesize(
                    model=model,
                    text=text,
                    audio_path=audio_file,
                    vocoder=vocoder,
                    split_text=(True if len(text) >= 160 else False)
                )
            except Exception as e:
                print("Error: %s" % e)
        else:
            print("Exiting program...")
        
if __name__ == "__main__":
    main()