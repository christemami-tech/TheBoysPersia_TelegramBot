import os
import telebot
from config import CHANNELS, movies

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def check_membership(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

@bot.message_handler(content_types=['video'])
def get_video(message):
    file_id = message.video.file_id
    bot.send_message(message.chat.id, file_id)

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()

    if len(args) > 1:
        movie_id = args[1]

        if not check_membership(message.from_user.id):
            markup = telebot.types.InlineKeyboardMarkup()

            for ch in CHANNELS:
                username = ch.replace("@", "")
                markup.add(
                    telebot.types.InlineKeyboardButton(
                        "📢 عضویت در کانال",
                        url=f"https://t.me/{username}"
                    )
                )

            bot.send_message(
                message.chat.id,
                "❌ برای دریافت فیلم باید عضو کانال‌ها باشید",
                reply_markup=markup
            )
            return

        bot.send_message(message.chat.id, "🎬 در حال ارسال فیلم...")

        bot.send_message(
            message.chat.id,
            movies.get(movie_id, "❌ فیلم پیدا نشد")
        )

    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("🎬 دریافت فیلم", callback_data="go")
        markup.add(btn)

        bot.send_message(
            message.chat.id,
            "👋 خوش آمدید",
            reply_markup=markup
        )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "go":
        bot.send_message(call.message.chat.id, "از لینک فیلم استفاده کن:\n\nhttps://t.me/TheBoysPersiaBot?start=film1")

bot.polling()
