import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import yt_dlp

# جلب التوكن من متغيرات البيئة (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# القناة المطلوبة
REQUIRED_CHANNEL = "@supreme_choice"


# التحقق من الاشتراك
async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        if member.status in ["left", "kicked"]:
            return False
        return True
    except Exception:
        return False


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
        [InlineKeyboardButton("✅ تحققت من الاشتراك", callback_data="verify")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 مرحباً! قبل استخدام البوت، اشترك في القناة التالية:", reply_markup=reply_markup)


# التحقق من الاشتراك
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if await check_subscription(user_id, context):
        await query.edit_message_text("✅ شكراً لاشتراكك! أرسل لي رابط فيديو لتحميله.")
    else:
        await query.edit_message_text("❌ لم تشترك بعد في القناة.")


# استقبال روابط الفيديو
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not await check_subscription(user_id, context):
        await update.message.reply_text("⚠️ يجب أن تشترك أولاً في القناة لاستخدام البوت.")
        return

    url = update.message.text
    await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {"outtmpl": "%(title)s.%(ext)s", "format": "mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(filename, "rb"))
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ: {e}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video))

    app.run_polling()


if __name__ == "__main__":
    main()