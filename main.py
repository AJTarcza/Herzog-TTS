from synthesis.synthesize import *
import os
import discord
import time
from dotenv import load_dotenv

# Constants
HOME = os.path.expanduser("~")
APP_PATH = HOME + "\Desktop\Herzog-TTS"
MODEL = APP_PATH + "\Model\Werner_Herzog\Werner_Herzog"
VOCODER_PATH = APP_PATH + "\Vocoder\Pretrained"
VOCODER_MODEL = VOCODER_PATH + "\g_02500000"
VOCODER_CONFIG = VOCODER_PATH + "\config.json"
AUDIO_PATH = APP_PATH + "\Audio"

model = None
vocoder = None

# Read environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX')

client = discord.Client()

@client.event
async def on_message(message):
    tokens = message.content.split()

    # Ignore the message if it isn't relevant
    if(message.author.bot or tokens[0].lower() != PREFIX):
        return
       
    # Channel the message was sent from
    channel = message.channel
    
    # Send an acknowledgement message to show that the bot is actually doing something
    ack_msg = await channel.send("Generating audio...")
        
    # Strip the prefix from the message
    text = message.content.replace(tokens[0] + " ", '')
    
    # Audio file path and name
    audio_file = AUDIO_PATH + "/%s.wav" % (time.time() * 1000)
    
    # Run the synthesizer
    synthesize(
        model=model,
        text=text,
        audio_path=audio_file,
        vocoder=vocoder,
        split_text=(True if len(text) >= 160 else False)
    )
    
    # Create the file object for messaging
    try:
        file = discord.File(audio_file)
    except:
        print("Error creating file")
        return
       
    # Remove the acknowledgement message to prevent clutter
    await ack_msg.delete()
    
    # Send the audio clip to the channel
    await channel.send(file=file, content=text)
    
    # Delete the file
    if(os.path.exists(audio_file)):
       os.remove(audio_file)

@client.event
async def on_ready():
    assert os.path.isfile(MODEL), "Model not found"
    assert os.path.isfile(VOCODER_MODEL), "vocoder model not found"
    
    if(not os.path.isdir(AUDIO_PATH)):
        os.mkdir(AUDIO_PATH)

    global model
    global vocoder
    
    model = load_model(MODEL)
    vocoder = Hifigan(VOCODER_MODEL, VOCODER_CONFIG)

    print(f'{client.user} is ready')
    
client.run(TOKEN)