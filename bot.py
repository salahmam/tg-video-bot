import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import yt_dlp

TOKEN = "ضع_توكن_البوت_هنا"
CHANNEL_USERNAME = "@supreme_choice"  # غيّرها لاسم قناتك

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
user_choice = {}

# دالة التحقق من الاشتراك
async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# القائمة الرئيسية
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    keyboard = [
        [InlineKeyboardButton("📱 سناب + تيك توك", callback_data="snap_tiktok")],
        [InlineKeyboardButton("📷 انستا + فيسبوك", callback_data="insta_facebook")],
        [InlineKeyboardButton("🎬 يوتيوب", callback_data="youtube")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 أهلاً بك!\nاختر المنصة التي تريد التحميل منها:"

    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

# دالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not await check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check_sub")]
        ]
        await update.message.reply_text("🚨 يجب الاشتراك بالقناة قبل الاستخدام:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await main_menu(update, context)

# تحميل من يوتيوب
def download_youtube(url, quality):
    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
        "quiet": True,
        "noplaylist": True,
        "outtmpl": "video.mp4"
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return "video.mp4", info.get("title", "video")

# استقبال الأزرار
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # تحقق من الاشتراك أولاً
    if query.data != "check_sub" and not await check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check_sub")]
        ]
        await query.edit_message_text("🚨 يجب الاشتراك بالقناة قبل الاستخدام:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    await query.answer()

    if query.data == "snap_tiktok":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text("📩 أرسل رابط من سناب أو تيك توك للتحميل.", reply_markup=InlineKeyboardMarkup(keyboard))
        user_choice[user_id] = "snap_tiktok"

    elif query.data == "insta_facebook":
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text("📩 أرسل رابط من انستا أو فيسبوك للتحميل.", reply_markup=InlineKeyboardMarkup(keyboard))
        user_choice[user_id] = "insta_facebook"

    elif query.data == "youtube":
        keyboard = [
            [InlineKeyboardButton("360p", callback_data="yt_360")],
            [InlineKeyboardButton("720p", callback_data="yt_720")],
            [InlineKeyboardButton("1080p", callback_data="yt_1080")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ]
        await query.edit_message_text("🎬 اختر دقة الفيديو:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("yt_"):
        quality = int(query.data.split("_")[1])
        user_choice[user_id] = f"youtube_{quality}"
        keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="back")]]
        await query.edit_message_text(f"📩 أرسل رابط يوتيوب وسيتم تحميله بجودة {quality}p.", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "back":
        await main_menu(update, context, edit=True)

    elif query.data == "check_sub":
        if await check_subscription(user_id, context):
            await main_menu(update, context, edit=True)
        else:
            await query.edit_message_text("🚨 لم يتم العثور على اشتراكك، اشترك وحاول مرة ثانية.")

# استقبال الروابط
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    url = update.message.text.strip()

    if not await check_subscription(user_id, context):
        keyboard = [
            [InlineKeyboardButton("📢 اشترك بالقناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check_sub")]
        ]
        await update.message.reply_text("🚨 يجب الاشتراك بالقناة قبل الاستخدام:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if user_id not in user_choice:
        await update.message.reply_text("⚠️ أولاً اختر المنصة من زر /start")
        return

    choice = user_choice[user_id]

    try:
        if choice.startswith("youtube_"):
            quality = choice.split("_")[1]
            await update.message.reply_text(f"⏳ يتم تحميل الفيديو من يوتيوب بجودة {quality}p...")
            file_path, title = download_youtube(url, quality)
            await update.message.reply_video(video=open(file_path, "rb"), caption=f"🎬 {title}")

        elif choice == "snap_tiktok":
            await update.message.reply_text("⏳ جاري تحميل الفيديو...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                await update.message.reply_video(video=response.content)
            else:
                await update.message.reply_text("❌ لم أتمكن من تحميل الرابط.")

        elif choice == "insta_facebook":
            await update.message.reply_text("⏳ جاري تحميل الفيديو...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                await update.message.reply_video(video=response.content)
            else:
                await update.message.reply_text("❌ لم أتمكن من تحميل الرابط.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ: {e}")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🚀 البوت يعمل الآن...")
    app.run_polling()

if __name__ == "__main__":
    main()