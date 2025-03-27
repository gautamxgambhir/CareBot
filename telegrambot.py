import os
import logging
import time
from dotenv import load_dotenv
import together
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')

# Initialize Together API client
client = together.Together(api_key=API_KEY)

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

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

# Command: Start chat session
async def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if chat_id in active_sessions:
        await update.message.reply_text("A chat session is already active in this chat!")
    else:
        active_sessions[chat_id] = True
        await update.message.reply_text("Care Bot is ready to assist you! Type your concerns, and I'll respond. Use /stop to end the session.")

# Command: Stop chat session
async def stop(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    if chat_id in active_sessions:
        del active_sessions[chat_id]
        await update.message.reply_text("Care Bot session ended. Take care and stay strong!")
    elif user_id in dm_sessions:
        del dm_sessions[user_id]
        await update.message.reply_text("Care Bot session ended. Take care and stay strong!")
    else:
        await update.message.reply_text("No active chat session in this chat.")

# Command: Restart chat session
async def restart(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    if chat_id in active_sessions:
        del active_sessions[chat_id]
        await update.message.reply_text("Chat session ended. Starting a new session...")
        active_sessions[chat_id] = True
        await update.message.reply_text("New chat session started! Type your concerns, and I'll respond. Use /stop to end the session.")
    elif user_id in dm_sessions:
        del dm_sessions[user_id]
        await update.message.reply_text("Chat session ended. Starting a new session in DM...")
        dm_sessions[user_id] = True
        await update.message.reply_text("New chat session started in DM! Type your concerns, and I'll respond. Use /stop to end the session.")
    else:
        await update.message.reply_text("No active chat session to restart. Use /start to begin a new session.")

# Command: Start DM chat session
async def dm(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in dm_sessions:
        await update.message.reply_text("You already have an active chat session in DM!")
    else:
        dm_sessions[user_id] = True
        await update.message.reply_text("Care Bot session started in DM! Type your concerns, and I'll respond. Use /stop to end the session.")

# Message handler
async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    if chat_id in active_sessions or user_id in dm_sessions:
        try:
            response = chatbot_response(update.message.text)
            await update.message.reply_text(response)
        except Exception as e:
            logging.error(f"Error: {e}")
            await update.message.reply_text("Sorry, I couldn't process your request. Please try again later.")

# Main function to run the bot
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("dm", dm))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    while True:
        try:
            print("Starting the bot...")
            print("Bot started")
            app.run_polling()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Restarting the bot in 1 second...")
            time.sleep(1)

if __name__ == "__main__":
    main()
