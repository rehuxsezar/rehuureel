import os
import logging
import instaloader
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Replace 'YOUR_BOT_TOKEN' with your actual Telegram bot token
TOKEN = '7502592198:AAHGB7TxO367eU30hxgm2edQu_CTIMPH67M'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize Instaloader
L = instaloader.Instaloader()

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an Instagram Reel link, and I'll download it for you!")

# Function to download Instagram Reel using Instaloader
def download_reel(instagram_url: str) -> str:
    try:
        shortcode = instagram_url.split('/')[-2]
        L.download_post(instaloader.Post.from_shortcode(L.context, shortcode), target=shortcode)
        video_filename = next((f for f in os.listdir(shortcode) if f.endswith('.mp4')), None)
        if video_filename:
            return os.path.join(shortcode, video_filename)
    except Exception as e:
        logging.error(f"Failed to download reel: {e}")
    return None

# Message handler for processing Instagram Reel links
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    if "instagram.com/reel" in message_text:
        await update.message.reply_text("Processing your Reel link...")
        video_path = download_reel(message_text)
        if video_path:
            try:
                with open(video_path, 'rb') as video_file:
                    await update.message.reply_video(video=InputFile(video_file))
                await update.message.reply_text("Here’s your Reel!")
                # Clean up downloaded files
                os.remove(video_path)
                os.rmdir(os.path.dirname(video_path))
            except Exception as e:
                await update.message.reply_text(f"An error occurred: {e}")
        else:
            await update.message.reply_text("Couldn’t download the video. The link might be invalid, private, or an error occurred during downloading.")
    else:
        await update.message.reply_text("Please send a valid Instagram Reel link (e.g., https://www.instagram.com/reel/...).")

# Main function to set up the bot
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()