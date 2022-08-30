## General info
This project is a [Werner Herzog](https://en.wikipedia.org/wiki/Werner_Herzog) Text-to-Speech application implemented using a discord bot for user input.

## Acknowledgements
Voice model training and synthesis were both accomplished using [BenAAndrew's Voice Cloning App](https://github.com/BenAAndrew/Voice-Cloning-App)
	
## Setup
To run this project, install it locally using pip to fetch the python requirements and git lfs to fetch the voice and synthesis models:
```
$ pip install -r requirements.txt
$ git lfs install
$ git lfs fetch --all
```
**NOTE: If git lfs fails to fetch the files due to reaching a data quota then they can be manually downloaded from here:**
- [Voice Model](https://drive.google.com/file/d/1fbw2C65xX2WrW4HLlQAm7tMKd0pzQ2W9/view?usp=sharing) [Overwrite file in /Model/Werner_Herzog/]
- [Vocoder Model](https://drive.google.com/file/d/1KQdFg3mWqeI0UsVNuOy0Wq5k9Donqtnn/view?usp=sharing) [Overwrite file in /Vocoder/Pretrained/]

Once this is done, edit the .env-EXAMPLE file with the appropriate information and rename it to just .env and start the bot using the command:
```
$ python main.py
```
## Usage

To interact with the bot, you can either invite it to a server and send messages to it using the COMMAND_PREFIX defined in the .env file, or you can send a direct message to HerzogTTS#4071 with the desired text.

Example using public server:
```
~werner This text was sent from a server text channel
```
Example using direct message:
```
This text was sent from a direct message
```