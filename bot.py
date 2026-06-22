import os
import telebot
from telebot import types
from config import CHANNELS, movies
from admin import is_admin, add_admin, remove_admin

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ======================
# چک عضویت
# ======================
def check_membership(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# ======================
# دکمه عضویت
# ======================
def join_markup():
    markup = types.InlineKeyboardMarkup()

    for ch in CHANNELS:
        username = ch.replace("@", "")
        markup.add(
            types.InlineKeyboardButton(
                "📢 عضویت در کانال",
                url=f"https://t.me/{username}"
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_membership"
        )
    )

    return markup

# ======================
# گرفتن فایل فقط برای ادمین
# ======================
@bot.message_handler(content_types=['video', 'photo', 'audio', 'document'])
def get_file(message):

    if not is_admin(message.from_user.id):
        return

    file_id = None

    if message.content_type == 'video':
        file_id = message.video.file_id
    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.content_type == 'audio':
        file_id = message.audio.file_id
    elif message.content_type == 'document':
        file_id = message.document.file_id

    bot.send_message(message.chat.id, f"📌 FILE ID:\n{file_id}")

# ======================
# پنل ادمین
# ======================
@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "❌ دسترسی ندارید")
        return

    bot.send_message(
        message.chat.id,
        "🧑‍💼 پنل ادمین:\n\n/add 123456789 ➜ اضافه کردن ادمین\n/remove 123456789 ➜ حذف ادمین"
    )

# ======================
# اضافه کردن ادمین
# ======================
@bot.message_handler(commands=['add'])
def add(message):

    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.split()[1])
        add_admin(user_id)
        bot.send_message(message.chat.id, f"✅ اضافه شد: {user_id}")
    except:
        bot.send_message(message.chat.id, "❌ فرمت اشتباه")

# ======================
# حذف ادمین
# ======================
@bot.message_handler(commands=['remove'])
def remove(message):

    if not is_admin(message.from_user.id):
        return

    try:
        user_id = int(message.text.split()[1])
        remove_admin(user_id)
        bot.send_message(message.chat.id, f"❌ حذف شد: {user_id}")
    except:
        bot.send_message(message.chat.id, "❌ فرمت اشتباه")

# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(message):

    args = message.text.split()

    if len(args) > 1:
        movie_id = args[1]

        if not check_membership(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "🎀 برای استفاده از ربات باید عضو کانال‌ها باشید:",
                reply_markup=join_markup()
            )
            return

        bot.send_message(message.chat.id, "🎬 در حال ارسال فیلم...")

        bot.send_video(
            message.chat.id,
            movies.get(movie_id, "❌ فیلم پیدا نشد")
        )

    else:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("🎬 دریافت فیلم", callback_data="go")
        markup.add(btn)

        bot.send_message(
            message.chat.id,
            "👋 خوش آمدید",
            reply_markup=markup
        )

# ======================
# CALLBACK
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "go":
        bot.send_message(
            call.message.chat.id,
            "از لینک فیلم استفاده کن:\n\nhttps://t.me/TheBoysPersiaBot?start=film1"
        )

    elif call.data == "check_membership":

        if check_membership(call.from_user.id):
            bot.send_message(call.message.chat.id, "🎬 تایید شد! در حال ارسال فیلم...")

            bot.send_video(
                call.message.chat.id,
                list(movies.values())[0]
            )

        else:
            bot.send_message(
                call.message.chat.id,
                "❌ هنوز عضو همه کانال‌ها نیستی!",
                reply_markup=join_markup()
            )

bot.polling()
