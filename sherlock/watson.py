# __________                  __             __     ________             .___ 
# \______   \  ____    ____  |  | __  ____ _/  |_  /  _____/   ____    __| _/ 
#  |       _/ /  _ \ _/ ___\ |  |/ /_/ __ \\   __\/   \  ___  /  _ \  / __ |  
#  |    |   \(  <_> )\  \___ |    < \  ___/ |  |  \    \_\  \(  <_> )/ /_/ |  
#  |____|_  / \____/  \___  >|__|_ \ \___  >|__|   \______  / \____/ \____ |  
#         \/              \/      \/     \/               \/              \/  
#
# Discord bot for Sherlock by RocketGod
# Edit config.json and run watson.py after the bot has been invited to your Discord server
# Use !sherlock <username> on your Discord Server
# Arguments like (!sherlock --help) or (!sherlock --nsfw rocketgod) work fine
#
# https://github.com/RocketGod-git/watson

import discord
from discord.ext import commands
import os
import json
import asyncio
import platform
import time

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Function to execute the Sherlock command and return the result as a string
async def execute_sherlock(ctx, *args):
    python_interpreter = "python3" if platform.system() == "Linux" else "python"
    username = None if args[-1] == "--help" else args[-1]
    filename = f"{username}.txt" if username else None
    
    # Check if the file already exists and get its last modified time
    if filename and os.path.exists(filename):
        last_modified_time = os.path.getmtime(filename)
    else:
        last_modified_time = None

    command = [python_interpreter, "sherlock.py"] + list(args)
    print(f"Sending command to sherlock.py: {' '.join(command)}")
    process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    print(f"Command output: {stdout.decode()}")
    print(f"Command error output: {stderr.decode()}")

    if process.returncode != 0:
        print(f"An error occurred while executing the command: {stderr.decode()}")
        await ctx.send(f"An error occurred while executing the command: {stderr.decode()}")
        return

    # Wait for the file to be updated
    if filename:
        while last_modified_time == os.path.getmtime(filename):
            time.sleep(1)

    print(f"Sherlock execution finished for username {username if username else 'help'}.")

    # If --help is used, return stdout. Otherwise, return None.
    return stdout.decode() if "--help" in args else None

# Coroutine for the spinner
async def spinner(ctx, username):
    spinner = "|/-\\"
    message = await ctx.send(f"Searching for `{username}` {spinner[0]}")
    print(f"Started searching for `{username}`.")
    for i in range(100):  # Adjusted the speed of spinner by increasing sleep time and reducing iterations
        await asyncio.sleep(0.5)
        await message.edit(content=f"Searching for `{username}` {spinner[i % len(spinner)]}")
    await message.edit(content=f"Search for `{username}` completed.")
    print(f"Search for `{username}` completed.")

# Bot command to search for a username on social networks using Sherlock
@bot.command()
@commands.cooldown(5, 60.0, commands.BucketType.user)
async def sherlock(ctx, *args):
    if not args:
        print("Arguments not specified.")
        await ctx.send("You must specify some arguments.")
        return

    username = None if args[-1] == "--help" else args[-1]
    print(f"Executing Sherlock for username {username if username else 'help'}.")

    if username:
        task2 = asyncio.create_task(spinner(ctx, username))

    help_output = await execute_sherlock(ctx, *args)
    
    # Sending the results to the same Discord channel
    print("Sending Sherlock result to Discord channel.")
    
    if username:
        with open(f"{username}.txt", "r") as f:
            output = f.read()
    else:
        output = help_output  # Use the stdout from --help.

    # Break the output into chunks that are small enough for Discord
    chunks = [output[i:i+2000] for i in range(0, len(output), 2000)]

    for chunk in chunks:
        await ctx.send(chunk)

    # Then wait for the spinner task to finish
    if username:
        await task2

# Command to handle errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        print("An error occurred while executing the command.")
        await ctx.send("An error occurred while executing the command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        print("Username not specified.")
        await ctx.send("You must specify a username.")
    elif isinstance(error, commands.CommandOnCooldown):
        print("Command on cooldown.")
        await ctx.send("You're doing that too often. Please wait a while before trying again.")

# Load the bot token
with open("config.json") as f:
    config = json.load(f)
    token = config.get("discord_bot_token")

# Run the bot
try:
    print("Starting the bot.")
    bot.run(token)
except Exception as e:
    print(f"Could not start the bot: {e}")