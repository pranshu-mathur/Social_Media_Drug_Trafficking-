import json
import logging
from datetime import datetime
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler

# Define the path for user activity JSON
USER_ACTIVITY_FILE = 'user_activity.json'

# Load the narcotics list from CSV
import pandas as pd
narcotics_df = pd.read_csv("common_narcotics_list.csv")
narcotic_keywords = set(narcotics_df['Narcotic_Name'].str.lower())

# Define the whitelist for users
WHITELIST_USERS = {"Arrnnavv", "PranshuIsGreat"}


ADMIN_CHAT_ID = 965616028 

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Load the model and tokenizer
model = DistilBertForSequenceClassification.from_pretrained(r"C:\Users\Pranshu M\Desktop\Project\Major Proj\Chatbot\trained_model")
tokenizer = DistilBertTokenizerFast.from_pretrained(r"C:\Users\Pranshu M\Desktop\Project\Major Proj\Chatbot\trained_model")

# Load or initialize user activity data
def load_user_activity():
    try:
        # Try loading existing data if the file exists
        with open(USER_ACTIVITY_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, return an empty dictionary
        logging.warning(f"{USER_ACTIVITY_FILE} not found. Creating a new one.")
        return {}

# Save user activity data to the JSON file
def save_user_activity(activity_data):
    try:
        with open(USER_ACTIVITY_FILE, 'w') as file:
            json.dump(activity_data, file, indent=4)
        logging.info(f"{USER_ACTIVITY_FILE} saved successfully.")
    except Exception as e:
        logging.error(f"Error saving {USER_ACTIVITY_FILE}: {e}")

# Check if the message contains narcotics keywords
def check_for_narcotics(message_text: str) -> list:
    message_words = message_text.lower().split()
    flagged_words = [word for word in message_words if word in narcotic_keywords]
    return flagged_words

# Predict the suspicion level of the message
def predict_suspicion(text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()

    class_map = {0: "Safe", 1: "Suspicious", 2: "Highly Suspicious"}
    return class_map.get(predicted_class, "Safe")

# Handle messages from users
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return  

    text = update.message.text
    user = update.effective_user.username or f"id:{update.effective_user.id}"

    # Log the chat ID to ensure it's correct
    chat_id = update.message.chat.id
    logging.info(f"Message received from chat ID: {chat_id}")

    # Ignore users not in whitelist
    if user not in WHITELIST_USERS:
        return

    # Load user activity data from JSON file
    activity_data = load_user_activity()

    # Check for narcotics and suspicion
    flagged_words = check_for_narcotics(text)
    suspicion = predict_suspicion(text)

    # Prepare activity entry
    activity_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": text,
        "flagged_keywords": flagged_words,
        "suspicion_level": suspicion,
        "alerted": False
    }

    # If narcotics are found or the message is suspicious
    if flagged_words or suspicion != "Safe":
        # Log the activity for the user
        if user not in activity_data:
            activity_data[user] = []

        activity_data[user].append(activity_entry)

        # Save the updated user activity
        save_user_activity(activity_data)

        # Send alerts to the admin
        alert_msg = (
            f"🚨 *Alert!*\n"
            f"User: @{user}\n"
            f"Flagged Keywords: {', '.join(flagged_words)}\n"
            f"Suspicion Level: {suspicion}\n"
            f"Message: {text}"
        )
        logging.info(alert_msg)
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=alert_msg, parse_mode='Markdown')
            logging.info(f"Alert sent to admin chat ID: {ADMIN_CHAT_ID}")
        except Exception as e:
            logging.error(f"Error sending message to admin: {e}")

# Command to get the chat ID
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    logging.info(f"Message received from chat ID: {chat_id}")
    await update.message.reply_text(f"Chat ID: {chat_id}")

# Main function to set up the bot
def main():
    TELEGRAM_BOT_TOKEN = "7788703216:AAGbdSGf-tuDxfbFRyLfVWuSDfc0Q-amTAY"
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(CommandHandler('start', get_chat_id))
    logging.info("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()
