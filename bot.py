import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View
import json
import os
from dotenv import load_dotenv
from art import text2art  
from colorama import Fore, Style, init

# Load .env file
load_dotenv()

TOKEN = os.getenv('TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))  
ROLE_ID = int(os.getenv('ROLE_ID'))   

# Name of the responses file
RESPONSE_FILE = 'responses.json'

# Default responses to include in the file
default_responses = {
    "السلام عليكم": "وعليكم السلام",
    "مرحبا": "مرحبا بك",
    "أهلا": "أهلاً بك!",
    "كيف حالك؟": "أنا بخير، شكراً لك!",
    "وداعاً": "إلى اللقاء!",
    "Hello": "Hello",
    "Welcome": "Welcome",
    "How are you": "Fine, thank you",
    "Goodbye": "Goodbye"
}

# Check if the responses file exists, if not, create it
def create_default_responses():
    if not os.path.exists(RESPONSE_FILE):
        with open(RESPONSE_FILE, 'w', encoding='utf-8') as file:
            json.dump(default_responses, file, ensure_ascii=False, indent=4)
        print(f"Created the file {RESPONSE_FILE} successfully.")
    else:
        print(f"The file {RESPONSE_FILE} already exists.")

# Load responses from JSON file
def load_responses(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

# Save responses to JSON file
def save_responses(filename, responses):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(responses, file, ensure_ascii=False, indent=4)

# Set up the client
intents = discord.Intents.default()
intents.message_content = True  
intents.guilds = True
intents.members = True  
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    try:
        # Create ASCII Art text for "Data Team Skoda"
        ascii_art_text = text2art("Wick® Studio")
        create_default_responses()
        # Register commands in the specified guild
        bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))

        # Print the ASCII Art text in the console with light color
        print(Fore.LIGHTCYAN_EX + ascii_art_text + Style.RESET_ALL)
        print(Fore.LIGHTGREEN_EX + f"Logged in as {bot.user}" + Style.RESET_ALL)

        # Change bot presence
        await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.listening, name="Wick® Studio"))
    except Exception as e:
        print(Fore.LIGHTRED_EX + f"Error in on_ready event: {e}" + Style.RESET_ALL)

@bot.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the message contains text that needs a response
    responses = load_responses(RESPONSE_FILE)
    response_text = responses.get(message.content)
    if response_text:
        # Mention the user who sent the message
        mention = message.author.mention
        response_message = f"{mention} {response_text}"
        await message.channel.send(response_message)
    
    # Make sure to process bot commands
    await bot.process_commands(message)

# Add slash command to add a new response
@bot.tree.command(name="addresponse", description="Add a new response")
async def add_response(interaction: discord.Interaction, trigger: str, response: str):
    # Check guild
    if interaction.guild.id != GUILD_ID:
        await interaction.response.send_message("This command is not enabled in this guild.")
        return

    # Get the member
    member = interaction.guild.get_member(interaction.user.id)
    if member is None:
        await interaction.response.send_message("I could not find your membership in this guild.")
        return

    # Check the role
    role = discord.utils.get(interaction.guild.roles, id=ROLE_ID)
    if role not in member.roles:
        await interaction.response.send_message("You do not have the required role to use this command.")
        return
    
    # Load current responses
    responses = load_responses(RESPONSE_FILE)
    
    # Add the new response
    responses[trigger] = response
    
    # Save updated responses to the file
    save_responses(RESPONSE_FILE, responses)
    
    await interaction.response.send_message(f'Added response: "{trigger}" -> "{response}"')

# Create a dropdown list for selecting the response to be deleted
class ResponseSelect(Select):
    def __init__(self, responses):
        options = [discord.SelectOption(label=key, value=key) for key in responses.keys()]
        super().__init__(placeholder="Select the response you want to delete", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_response = self.values[0]
        responses = load_responses(RESPONSE_FILE)
        if selected_response in responses:
            del responses[selected_response]
            save_responses(RESPONSE_FILE, responses)
            await interaction.response.send_message(f'Deleted response: "{selected_response}"')
        else:
            await interaction.response.send_message(f'Response not found: "{selected_response}"')

# Add slash command to show dropdown list for response removal
@bot.tree.command(name="removeresponse", description="Remove an existing response")
async def remove_response(interaction: discord.Interaction):
    # Check guild
    if interaction.guild.id != GUILD_ID:
        await interaction.response.send_message("This command is not enabled in this guild.")
        return

    # Get the member
    member = interaction.guild.get_member(interaction.user.id)
    if member is None:
        await interaction.response.send_message("I could not find your membership in this guild.")
        return

    # Check the role
    role = discord.utils.get(interaction.guild.roles, id=ROLE_ID)
    if role not in member.roles:
        await interaction.response.send_message("You do not have the required role to use this command.")
        return

    # Load current responses
    responses = load_responses(RESPONSE_FILE)
    
    # Create a dropdown list for selecting the response to delete
    select = ResponseSelect(responses)
    view = View()
    view.add_item(select)

    await interaction.response.send_message("Select the response you want to delete from the list:", view=view)

# Run the bot
bot.run(TOKEN)
