import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

CHANNELS = ["@TheBoysinTelegram", "@DrDoctorMeme"]

movies = {
    "film1": "BAACAgQAAxkBAAMIajkh_DWv2QFg47JFNg1uv9x8LMoAApUcAAKn6sFRm5aI2hDZHmw8BA"
}

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
    bot.send_message(message.chat.id, f"FILE ID:\n{file_id}")

def start_menu():
    markup = telebot.types.InlineKeyboardMarkup()

    btn1 = telebot.types.InlineKeyboardButton("🎬 دریافت فیلم", callback_data="get_film")
    btn2 = telebot.types.InlineKeyboardButton("📢 کانال‌ها", callback_data="channels")

    markup.add(btn1)
    markup.add(btn2)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎀 خوش آمدید\nاز دکمه‌ها استفاده کنید:",
        reply_markup=start_menu()
    )

@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "channels":
        text = "📢 برای استفاده باید عضو این کانال‌ها شوید:\n\n"
        text += "\n".join(CHANNELS)

        bot.send_message(call.message.chat.id, text)

    elif call.data == "get_film":

        if not check_membership(call.from_user.id):
            markup = telebot.types.InlineKeyboardMarkup()

            btn = telebot.types.InlineKeyboardButton(
                "📢 رفتن به کانال‌ها",
                url=f"https://t.me/{CHANNELS[0].replace('@','')}"
            )

            markup.add(btn)

            bot.send_message(
                call.message.chat.id,
                "❌ برای استفاده باید عضو کانال‌ها شوید",
                reply_markup=markup
            )
            return

        bot.send_message(call.message.chat.id, "🎬 در حال ارسال فیلم...")

        bot.send_message(
            call.message.chat.id,
            movies["film1"]
        )

bot.polling()
