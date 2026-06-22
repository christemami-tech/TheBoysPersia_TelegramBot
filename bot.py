import os
import telebot
from telebot import types
from config import CHANNELS, movies, ADMIN_ID

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


# ======================
# چک ادمین
# ======================
def is_admin(user_id):
    return user_id == ADMIN_ID


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
# پیدا کردن slot خالی
# ======================
def get_next_slot(file_type):
    data = movies[file_type]

    i = 1
    while True:
        key = f"{file_type}{i}"
        if key not in data:
            return key
        i += 1


# ======================
# ذخیره فایل
# ======================
def save_file(file_type, file_id, name=None):
    if not name:
        name = get_next_slot(file_type)

    movies[file_type][name] = file_id
    return name


# ======================
# ارسال فایل
# ======================
def send_media(chat_id, file_type, file_id):

    if file_type == "video":
        bot.send_video(chat_id, file_id)

    elif file_type == "photo":
        bot.send_photo(chat_id, file_id)

    elif file_type == "audio":
        bot.send_audio(chat_id, file_id)

    elif file_type == "document":
        bot.send_document(chat_id, file_id)


# ======================
# پنل ادمین
# ======================
@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ دسترسی ندارید")

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("📤 افزودن فیلم", callback_data="add_video"))
    markup.add(types.InlineKeyboardButton("🖼 افزودن عکس", callback_data="add_photo"))
    markup.add(types.InlineKeyboardButton("🎧 افزودن صدا", callback_data="add_audio"))
    markup.add(types.InlineKeyboardButton("📁 افزودن فایل", callback_data="add_doc"))

    bot.send_message(message.chat.id, "🧑‍💼 پنل مدیریت:", reply_markup=markup)


# ======================
# حالت انتظار (برای آپلود)
# ======================
waiting = {}


# ======================
# callback پنل
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if not is_admin(call.from_user.id):
        return

    if call.data.startswith("add_"):
        file_type = call.data.split("_")[1]
        waiting[call.from_user.id] = file_type

        bot.send_message(
            call.message.chat.id,
            f"📥 حالا فایل {file_type} را ارسال کن"
        )


    elif call.data.startswith("get_"):
        parts = call.data.split("_")
        file_type = parts[1]
        name = parts[2]

        file_id = movies[file_type].get(name)

        if file_id:
            send_media(call.message.chat.id, file_type, file_id)
        else:
            bot.send_message(call.message.chat.id, "❌ پیدا نشد")


# ======================
# گرفتن فایل از ادمین
# ======================
@bot.message_handler(content_types=['video', 'photo', 'audio', 'document'])
def get_file(message):

    if not is_admin(message.from_user.id):
        return

    file_type = message.content_type
    file_id = None

    if file_type == "video":
        file_id = message.video.file_id
    elif file_type == "photo":
        file_id = message.photo[-1].file_id
    elif file_type == "audio":
        file_id = message.audio.file_id
    elif file_type == "document":
        file_id = message.document.file_id

    if message.from_user.id in waiting:
        t = waiting.pop(message.from_user.id)

        name = save_file(t, file_id)

        bot.send_message(
            message.chat.id,
            f"✅ ذخیره شد\nنوع: {t}\nنام: {name}"
        )
    else:
        bot.send_message(message.chat.id, "⚠️ اول از پنل نوع فایل رو انتخاب کن")


# ======================
# START کاربر
# ======================
@bot.message_handler(commands=['start'])
def start(message):

    args = message.text.split()

    if len(args) > 1:
        key = args[1]

        if not check_membership(message.from_user.id):
            return bot.send_message(message.chat.id, "عضو کانال‌ها شو")

        for t in movies:
            if key in movies[t]:
                send_media(message.chat.id, t, movies[t][key])
                return

        bot.send_message(message.chat.id, "❌ پیدا نشد")

    else:
        bot.send_message(message.chat.id, "👋 خوش آمدی")


bot.polling()
