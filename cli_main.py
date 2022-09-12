import os
import readline
import sys
from synthesis.synthesize import *
from string import punctuation as punct

# Paths
APP_PATH = os.path.dirname(os.path.realpath(__file__))
MODEL = os.path.join(APP_PATH, "Model", "Werner_Herzog", "Werner_Herzog")
VOCODER_MODEL = os.path.join(APP_PATH, "Vocoder", "Pretrained", "g_02500000")
VOCODER_CONFIG = os.path.join(APP_PATH, "Vocoder", "Pretrained", "config.json")
AUDIO_PATH = os.path.join(APP_PATH, "Audio")

EXIT_KEYWORD = "exit"

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