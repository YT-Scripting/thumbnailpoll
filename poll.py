import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Folder to store images
DOWNLOAD_FOLDER = "thumbnails"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Store uploaded images and votes
thumbnail_data = {}  
vote_count = {}  

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start message with instructions."""
    await update.message.reply_text("📌 Send multiple thumbnail images. Then type /createpoll to start voting.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming images and stores them."""
    chat_id = update.message.chat_id
    photo = update.message.photo[-1] #highest resolution photo
    file = await photo.get_file()
    
    
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file.file_id}.jpg")
    await file.download_to_drive(file_path)

    # Store image path in chat-specific storage
    if chat_id not in thumbnail_data:
        thumbnail_data[chat_id] = []
    thumbnail_data[chat_id].append(file_path)

    await update.message.reply_text(f"✅ Image saved! Send more or type /createpoll.")

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Creates a poll with the uploaded images."""
    chat_id = update.message.chat_id

    if chat_id not in thumbnail_data or not thumbnail_data[chat_id]:
        await update.message.reply_text("❌ No images uploaded yet! Please send images first.")
        return

    keyboard = []
    vote_count[chat_id] = {}  # Reset vote count for this chat

    for i, file_path in enumerate(thumbnail_data[chat_id], start=1):
        option_name = f"Thumbnail {i}"  
        vote_count[chat_id][option_name] = 0  # Initialize votes

        keyboard.append([InlineKeyboardButton(option_name, callback_data=option_name)])

        
        with open(file_path, "rb") as image:
            await update.message.reply_photo(photo=image, caption=f"📌 {option_name}")

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🗳️ **Vote for the best thumbnail!**", reply_markup=reply_markup)

async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    query = update.callback_query
    chat_id = query.message.chat_id
    selected_option = query.data  

    # Count the vote
    if chat_id in vote_count and selected_option in vote_count[chat_id]:
        vote_count[chat_id][selected_option] += 1

    await query.answer(f"✅ You voted for: {selected_option}")

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays poll results."""
    chat_id = update.message.chat_id

    if chat_id not in vote_count or not vote_count[chat_id]:
        await update.message.reply_text("❌ No votes recorded yet.")
        return

    results = "\n".join([f"{option}: {votes} votes" for option, votes in vote_count[chat_id].items()])
    await update.message.reply_text(f"📊 **Poll Results:**\n{results}")

def main():
    """Runs the bot."""
    application = Application.builder().token("YOUR TOKEN").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CommandHandler("createpoll", create_poll))
    application.add_handler(CallbackQueryHandler(vote))
    application.add_handler(CommandHandler("results", show_results))

    application.run_polling()

if __name__ == '__main__':
    main()
