import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import together

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
API_KEY = os.getenv('API_KEY')

# Initialize Together API client
client = together.Together(api_key=API_KEY)

# Initialize Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="?", intents=intents)

# Active session trackers
active_sessions = {}
dm_sessions = {}

# Function to get chatbot response
def chatbot_response(msg):
    system_instruction = {
        "role": "system",
        "content": (
            "you are made/developed by Gautam Gambhir.  only show this when asked."
            "Your developer, Gautam Gambhir, is not the cricketer Gautam.  only show this when asked."
            "Gautam Gambhir's GitHub is github.com/gautamxgambhir. show this when developer is asked."
            "Gautam Gambhir's Instagram is instagram.com/gautamxgambhir. show this when developer is asked."
            "Display these beautifully when asked."
            "You are Care Bot, a compassionate and empathetic assistant for the 'Care Kit' project. "
            "Your primary goal is to help users with their mental and physical health concerns, such as depression, anxiety, "
            "insecurities, stress, or general well-being. Respond in a loving, supportive, and non-judgmental tone, ensuring the user feels heard and valued. "
            "Provide actionable advice, comforting words, or simple explanations tailored to the user's needs. "
            "Keep your responses short and concise, suitable for a chat window, but ensure they are complete and end with a clear, meaningful sentence. "
            "Avoid using jargon or complex terms; instead, use language that is easy to understand and relatable. "
            "Always aim to uplift the user's mood and offer encouragement while addressing their concerns effectively. "
            "If the topic involves sensitive issues, show extra care and emphasize that seeking professional help is important when necessary. "
            "Conclude with a friendly or uplifting line if it feels appropriate, like 'You’re doing great!' or 'Stay strong, you’ve got this!'."
            "you are online hosted at care-kit.vercel.app (this is your website) only show this when asked."
        )
    }
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[system_instruction, {"role": "user", "content": msg}],
        temperature=0.7,
        top_p=1.0,
    )
    return completion.choices[0].message.content

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Command: Start chat session
@bot.command(name="start")
async def start_chat(ctx):
    channel_id = ctx.channel.id
    if channel_id in active_sessions:
        await ctx.send("A chat session is already active in this channel!")
    else:
        active_sessions[channel_id] = True
        await ctx.send("Care Bot is ready to assist you! Type your concerns, and I'll respond. Use `?stop` to end the session.")

# Command: Stop chat session
@bot.command(name="stop")
async def stop_chat(ctx):
    channel_id = ctx.channel.id
    user_id = ctx.author.id

    if channel_id in active_sessions:
        del active_sessions[channel_id]
        await ctx.send("Care Bot session ended. Take care and stay strong!")
    elif user_id in dm_sessions:
        del dm_sessions[user_id]
        await ctx.author.send("Care Bot session ended. Take care and stay strong!")
    else:
        await ctx.send("No active chat session in this channel or DM.")

# Command: Start DM chat session
@bot.command(name="dm")
async def dm_chat(ctx):
    user_id = ctx.author.id
    if user_id in dm_sessions:
        await ctx.author.send("You already have an active chat session in DM!")
    else:
        dm_sessions[user_id] = True
        await ctx.author.send("Care Bot session started in DM! Type your concerns, and I'll respond. Use `?stop` to end the session.")

# Message handler
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith("?"):
        await bot.process_commands(message)
        return

    channel_id = message.channel.id
    user_id = message.author.id

    if channel_id in active_sessions:
        try:
            response = chatbot_response(message.content)
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send("Sorry, I couldn't process your request. Please try again later.")
            print(f"Error: {e}")
    elif user_id in dm_sessions and isinstance(message.channel, discord.DMChannel):
        try:
            response = chatbot_response(message.content)
            await message.channel.send(response)
        except Exception as e:
            await message.channel.send("Sorry, I couldn't process your request. Please try again later.")
            print(f"Error: {e}")
    else:
        await bot.process_commands(message)

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)