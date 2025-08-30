import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# تشغيل اللوج
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# جلب التوكن من Render Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

# معرفات القنوات اللي لازم ينضم لها المستخدم
REQUIRED_CHANNELS = ["@https://t.me/supreme_choice", "@https://t.me/supreme_choice"]


# ✅ دالة التحقق من الاشتراك
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            logger.warning(f"خطأ في التحقق من {channel}: {e}")
            return False
    return True


# ✅ أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة 1", url="https://t.me/supreme_choice")],
                [InlineKeyboardButton("📢 اشترك بالقناة 2", url="https://t.me/supreme_choice")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 أهلاً بك في بوت التحميل.\n\n"
        "📌 يجب أن تشترك في القنوات التالية لتتمكن من استخدام البوت:",
        reply_markup=reply_markup
    )


# ✅ استقبال الروابط وتحميل الفيديو
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await update.message.reply_text("⚠️ يجب أن تشترك في القنوات أولاً قبل التحميل.")
        return

    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {
            "format": "mp4",
            "outtmpl": "%(title)s.%(ext)s"
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, "rb"))
        os.remove(file_name)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ حدث خطأ أثناء التحميل. تأكد من الرابط.")


# ✅ تشغيل البوت
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()


if __name__ == "__main__":
    main()
