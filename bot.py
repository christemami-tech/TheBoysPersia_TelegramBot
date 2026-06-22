import os
import telebot
from telebot import types
from config import CHANNELS, movies

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
# دکمه عضویت کانال‌ها + بررسی عضویت
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

    # دکمه سبز بررسی عضویت
    markup.add(
        types.InlineKeyboardButton(
            "✅ بررسی عضویت",
            callback_data="check_membership"
        )
    )

    return markup

# ======================
# گرفتن file_id (برای خودت)
# ======================
@bot.message_handler(content_types=['video'])
def get_video(message):
    file_id = message.video.file_id
    bot.send_message(message.chat.id, file_id)

# ======================
# /start
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
# دکمه‌ها
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # دکمه شروع
    if call.data == "go":
        bot.send_message(
            call.message.chat.id,
            "از لینک فیلم استفاده کن:\n\nhttps://t.me/TheBoysPersiaBot?start=film1"
        )

    # دکمه بررسی عضویت
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
