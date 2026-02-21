import os
import discord
from discord.ext import commands
from flask import Flask
from threading import Thread

# Flask setup for keeping the bot alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

if __name__ == '__main__':
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("No DISCORD_TOKEN found in environment variables.")