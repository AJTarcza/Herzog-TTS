from synthesis.synthesize import *
import os
import discord
from time import time
from dotenv import load_dotenv

# Constants
HOME = os.path.expanduser("~")
APP_PATH = os.path.join(HOME, "Desktop", "Herzog-TTS")
MODEL = os.path.join(APP_PATH, "Model", "Werner_Herzog", "Werner_Herzog")
VOCODER_MODEL = os.path.join(APP_PATH, "Vocoder", "Pretrained", "g_02500000")
VOCODER_CONFIG = os.path.join(APP_PATH, "Vocoder", "Pretrained", "config.json")
AUDIO_PATH = os.path.join(APP_PATH, "Audio")

# Environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX')

# Globals
model = None
vocoder = None

client = discord.Client()

@client.event
async def on_message(message):
    tokens = message.content.split()
    
    # Ignore the message if it isn't relevant
    if(message.author.bot or (message.guild and tokens[0].lower() != PREFIX.lower())):
        return
  
    # Strip the prefix from the message
    text = message.content.replace(PREFIX + " ", '')
    
    # Channel the message was sent from
    channel = message.channel
    
    # Check if text for synthesis is empty
    if(text.isspace() or text.lower() == PREFIX.lower()):
        await channel.send("Error! Text is empty")
        return
    
    # Send an acknowledgement message to show that the bot is actually doing something
    ack_msg = await channel.send("Generating audio...")
    
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
        print("Error synthesizing voice")
        await ack_msg.delete()
        await channel.send(e)
        return
    
    # Create the file object for messaging
    try:
        file = discord.File(audio_file)
    except:
        print("Error creating file")
        await ack_msg.delete()
        await channel.send("Error creating file")
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