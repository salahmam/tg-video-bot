import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# اقرأ التوكن من المتغير البيئي
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "@supreme_choice"  # قناة الاشتراك الإجباري

# ----------------------- START -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # تحقق من الاشتراك بالقناة
    member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
    if member.status not in ["member", "administrator", "creator"]:
        await update.message.reply_text(
            "⚠️ يجب عليك الاشتراك في القناة أولاً:\n"
            f"{CHANNEL_ID}\n\nثم اضغط /start"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📥 تحميل سناب & تيك توك", callback_data="snap_tiktok")],
        [InlineKeyboardButton("📥 تحميل انستا & فيسبوك", callback_data="insta_fb")],
        [InlineKeyboardButton("📥 تحميل يوتيوب", callback_data="youtube_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 أهلاً بك!\nاختر المنصة:", reply_markup=reply_markup)

# ----------------------- MAIN MENU HANDLER -----------------------
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "snap_tiktok":
        await query.edit_message_text("📥 أرسل رابط من **سناب أو تيك توك** للتحميل.")
    elif query.data == "insta_fb":
        await query.edit_message_text("📥 أرسل رابط من **انستغرام أو فيسبوك** للتحميل.")
    elif query.data == "youtube_menu":
        keyboard = [
            [InlineKeyboardButton("🎬 1080p", callback_data="yt_1080")],
            [InlineKeyboardButton("🎬 720p", callback_data="yt_720")],
            [InlineKeyboardButton("🎬 480p", callback_data="yt_480")],
            [InlineKeyboardButton("🎬 360p", callback_data="yt_360")],
            [InlineKeyboardButton("🎬 240p", callback_data="yt_240")],
            [InlineKeyboardButton("🎬 144p", callback_data="yt_144")],
            [InlineKeyboardButton("◀️ رجوع", callback_data="back_main")]
        ]
        await query.edit_message_text("اختر دقة الفيديو:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == "back_main":
        await start(update, context)

# ----------------------- YOUTUBE DOWNLOAD -----------------------
async def youtube_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    quality = query.data.split("_")[1]  # مثال yt_720 → 720

    context.user_data["yt_quality"] = quality
    await query.edit_message_text(
        f"🎬 اخترت دقة {quality}p.\n\n📩 الآن أرسل رابط اليوتيوب."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # إذا كان المستخدم اختار دقة من يوتيوب
    if "yt_quality" in context.user_data:
        quality = context.user_data["yt_quality"]
        await update.message.reply_text("⏳ جاري التحميل من يوتيوب...")

        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
            "outtmpl": "%(title)s.%(ext)s"
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(text, download=True)
                file_name = ydl.prepare_filename(info)

            await update.message.reply_video(video=open(file_name, "rb"))
            os.remove(file_name)

        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ: {e}")

        del context.user_data["yt_quality"]

    else:
        await update.message.reply_text("📩 أرسل رابط صحيح للتحميل.")

# ----------------------- MAIN -----------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_handler, pattern="^(snap_tiktok|insta_fb|youtube_menu|back_main)$"))
    app.add_handler(CallbackQueryHandler(youtube_download, pattern="^yt_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()