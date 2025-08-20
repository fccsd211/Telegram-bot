import os
import yt_dlp
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

BOT_TOKEN = "7821160960:AAF8H7Bn_78R9EPqjL_J2oa8OykcL4V8Vwo"

# Oxirgi qidiruv natijasini saqlash
last_query = {}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🎶 Qo‘shiq nomini yozing yoki YouTube/Instagram link tashlang!")

# Yuklab olish funksiyasi
def download_media(url, audio_only=False):
    ydl_opts = {
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }
    if audio_only:
        ydl_opts["format"] = "bestaudio/best"
    else:
        ydl_opts["format"] = "best"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if "entries" in info:
            info = info["entries"][0]
        filename = ydl.prepare_filename(info)
    return filename, info

async def handle_message(update: Update, context: CallbackContext):
    global last_query
    text = update.message.text.strip()

    if text.startswith("http://") or text.startswith("https://"):
        last_query[update.effective_user.id] = text
        keyboard = [["🎵 MP3", "🎬 Video"]]
        await update.message.reply_text("Qaysi formatda yuklab olishni xohlaysiz?", 
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    else:
        last_query[update.effective_user.id] = f"ytsearch:{text}"
        keyboard = [["🎵 MP3", "🎬 Video"]]
        await update.message.reply_text("Qaysi formatda yuklab olishni xohlaysiz?", 
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

async def choose_format(update: Update, context: CallbackContext):
    global last_query
    choice = update.message.text
    user_id = update.effective_user.id

    if user_id not in last_query:
        await update.message.reply_text("❌ Avval qo‘shiq nomi yoki link yuboring!")
        return

    query = last_query[user_id]

    try:
        if choice == "🎵 MP3":
            await update.message.reply_text("⬇️ MP3 yuklanmoqda, kuting...")
            file_path, info = download_media(query, audio_only=True)
            await update.message.reply_audio(audio=open(file_path, "rb"), title=info.get("title", ""))
        elif choice == "🎬 Video":
            await update.message.reply_text("⬇️ Video yuklanmoqda, kuting...")
            file_path, info = download_media(query, audio_only=False)
            await update.message.reply_video(video=open(file_path, "rb"), caption=info.get("title", ""))
        else:
            return

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Xato: {str(e)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("🎵 MP3|🎬 Video"), choose_format))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
