## General info
This project is a [Werner Herzog](https://en.wikipedia.org/wiki/Werner_Herzog) Text-to-Speech application that features two forms of user interaction, either through a Discord bot or Command Line Interface. 

## Acknowledgements
Voice model training and synthesis were both accomplished using [BenAAndrew's Voice Cloning App](https://github.com/BenAAndrew/Voice-Cloning-App).
	
## Installation
1. Clone this repository
2. Install [Python](https://www.python.org/) (version 3.9)
3. Install the required modules through pip using one of these commands:
	- **CUDA**
		- `pip install -r requirements.txt`
	- **CPU Only**
		- `pip install -r requirements-cpu.txt`
4. Fetch the voice and vocoder models using git lfs using these commands:
	```
	git lfs install
	git lfs fetch --all
	```
	**If git lfs fails to fetch the files due to reaching a data quota then they can be manually downloaded from here:**
	- [Voice Model](https://drive.google.com/file/d/1fbw2C65xX2WrW4HLlQAm7tMKd0pzQ2W9/view?usp=sharing) [Overwrite file in /Model/Werner_Herzog/]
	- [Vocoder Model](https://drive.google.com/file/d/1KQdFg3mWqeI0UsVNuOy0Wq5k9Donqtnn/view?usp=sharing) [Overwrite file in /Vocoder/Pretrained/]

## Running the Application
### Discord Bot
1. Edit `.env-EXAMPLE` with the appropriate information
2. Rename `.env-EXAMPLE` to just `.env`
3. Run `python bot_main.py`
4. Interact with the bot using one of these two methods:
	- Invite the bot to a server and send a message beginning with the `DISCORD_PREFIX` defined in the `.env` file in any chat the bot has access to as seen below:
		- `~werner This text was sent from a server text channel`
			
	- Send a direct message to the bot's Discord ID with the desired text as seen below:
		- `This text was sent from a direct message`

### Command Line Interface
1. Run `python cli_main.py`
2. Enter desired text using the console
3. Fetch generated audio clips from the `Audio` directory