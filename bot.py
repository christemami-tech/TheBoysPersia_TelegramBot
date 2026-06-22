import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# کانال‌ها رو اینجا عوض کن
CHANNELS = ["@TheBoysinTelegram", "t.me/+nP7TF4ffoCIwZTZh", "@DrDoctorMeme"]

# فیلم‌ها (بعداً file_id اینجا قرار می‌گیره)
movies = {
    "film1": "FILE_ID_HERE"
}

# بررسی عضویت در کانال‌ها
def check_membership(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# گرفتن file_id از ویدیو (برای خودت)
@bot.message_handler(content_types=['video'])
def get_video(message):
    file_id = message.video.file_id
    bot.send_message(message.chat.id, f"FILE ID:\n{file_id}")

# /start با لینک فیلم
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()

    # اگر لینک فیلم داشت
    if len(args) > 1:
        movie_id = args[1]

        if not check_membership(message.from_user.id):
            bot.send_message(message.chat.id, "🎀برای استفاده از ربات لطفا داخل کانالهای زیر عضو شوید:")
            return

        bot.send_message(message.chat.id, "🎬 در حال ارسال فیلم...")

        bot.send_message(
            message.chat.id,
            movies.get(movie_id, "🪖 ویدیو منقضی شده است")
        )
    else:
        bot.send_message(
            message.chat.id,
            "👋 خوش آمدید\nبرای دریافت فیلم از لینک استفاده کنید"
        )

bot.polling()
