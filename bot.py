import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# جلب التوكن من المتغيرات البيئية في Railway
TOKEN = os.getenv("BOT_TOKEN")

# معرف القناة المطلوب الاشتراك بها
CHANNEL_USERNAME = "@supreme_choice"  # عدله لقناتك

# دالة التحقق من الاشتراك
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# دالة البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚠️ يجب أن تشترك بالقناة أولاً لتستخدم البوت:", reply_markup=reply_markup)
        return

    keyboard = [
        [InlineKeyboardButton("📥 تحميل (سناب + تيك توك)", callback_data="download_snaptok")],
        [InlineKeyboardButton("📥 تحميل (انستغرام + فيسبوك)", callback_data="download_insta_fb")],
        [InlineKeyboardButton("🎬 تحميل يوتيوب", callback_data="youtube_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 أهلاً بك! اختر المنصة التي تريد التحميل منها:", reply_markup=reply_markup)

# القائمة الخاصة باليوتيوب
async def youtube_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🔽 دقة منخفضة", callback_data="yt_low")],
        [InlineKeyboardButton("🔼 دقة عالية", callback_data="yt_high")],
        [InlineKeyboardButton("🎨 دقة عالية + فلتر", callback_data="yt_high_filter")],
        [InlineKeyboardButton("✨ فلتر فقط", callback_data="yt_filter")],
        [InlineKeyboardButton("⬅️ رجوع", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("🎬 اختر دقة الفيديو أو الإجراء المطلوب:", reply_markup=reply_markup)

# التعامل مع الأزرار
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "download_snaptok":
        await query.edit_message_text("📥 أرسل رابط من سناب شات أو تيك توك للتحميل.")
    elif query.data == "download_insta_fb":
        await query.edit_message_text("📥 أرسل رابط من إنستغرام أو فيسبوك للتحميل.")
    elif query.data == "youtube_menu":
        await youtube_menu(update, context)
    elif query.data == "back_main":
        await start(update, context)
    else:
        await query.edit_message_text(f"✅ تم اختيار: {query.data}\n\nالآن أرسل الرابط للتحميل.")

# استقبال الروابط
async def handle_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text(f"📌 استلمت الرابط:\n{url}\n\n⚙️ جاري التحميل ... (محاكاة)")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_links))

    app.run_polling()

if __name__ == "__main__":
    main()