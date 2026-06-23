import os
import telebot
import time
import threading
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
# ارسال فایل + ویو + حذف 40 ثانیه
# ======================
def send_media(chat_id, key, item):

    if not item:
        bot.send_message(chat_id, "❌ فایل پیدا نشد")
        return

    # 👁 ویو
    item["views"] = item.get("views", 0) + 1
    views = item["views"]

    caption = f"👁 بازدید: {views}\n⏳ این فایل بعد از ۴۰ ثانیه حذف می‌شود"

    msg = None

    if item["type"] == "video":
        msg = bot.send_video(chat_id, item["file_id"], caption=caption)

    elif item["type"] == "photo":
        msg = bot.send_photo(chat_id, item["file_id"], caption=caption)

    elif item["type"] == "audio":
        msg = bot.send_audio(chat_id, item["file_id"], caption=caption)

    elif item["type"] == "document":
        msg = bot.send_document(chat_id, item["file_id"], caption=caption)

    else:
        bot.send_message(chat_id, "❌ نوع فایل ناشناخته")
        return

    # ⏳ حذف بعد 40 ثانیه
    def delete_later(chat_id, message_id):
        time.sleep(40)
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass

    threading.Thread(
        target=delete_later,
        args=(chat_id, msg.message_id),
        daemon=True
    ).start()


# ======================
# پنل ادمین
# ======================
def admin_panel_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Add File", callback_data="add"),
        types.InlineKeyboardButton("🗑 Delete File", callback_data="delete")
    )
    markup.add(
        types.InlineKeyboardButton("📋 List Files", callback_data="list")
    )
    return markup


# ======================
# حالت موقت
# ======================
waiting = {}  # user_id -> action


# ======================
# /admin
# ======================
@bot.message_handler(commands=['admin'])
def admin(message):

    if not is_admin(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ دسترسی ندارید")

    bot.send_message(message.chat.id, "🧑‍💼 پنل ادمین", reply_markup=admin_panel_markup())


# ======================
# callback ها
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if not is_admin(call.from_user.id):
        return

    # ➕ ADD
    if call.data == "add":
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("🎥 Video", callback_data="add_video"),
            types.InlineKeyboardButton("🖼 Photo", callback_data="add_photo"),
        )
        markup.add(
            types.InlineKeyboardButton("🎧 Audio", callback_data="add_audio"),
            types.InlineKeyboardButton("📁 Document", callback_data="add_document"),
        )

        bot.send_message(call.message.chat.id, "نوع فایل را انتخاب کن:", reply_markup=markup)


    elif call.data.startswith("add_"):
        file_type = call.data.split("_")[1]
        waiting[call.from_user.id] = {"action": "add", "type": file_type}

        bot.send_message(call.message.chat.id, f"📥 حالا فایل {file_type} را ارسال کن")


    # 📋 LIST
    elif call.data == "list":

        text = "📋 لیست فایل‌ها:\n\n"

        for k, v in movies.items():
            text += f"🔹 {k} → {v['type']} 👁 {v.get('views',0)}\n"

        bot.send_message(call.message.chat.id, text)


    # 🗑 DELETE
    elif call.data == "delete":

        markup = types.InlineKeyboardMarkup()

        for k, v in movies.items():
            markup.add(
                types.InlineKeyboardButton(
                    f"❌ {k}",
                    callback_data=f"del_{k}"
                )
            )

        bot.send_message(call.message.chat.id, "برای حذف انتخاب کن:", reply_markup=markup)


    elif call.data.startswith("del_"):
        key = call.data.split("_", 1)[1]

        if key in movies:
            del movies[key]
            bot.send_message(call.message.chat.id, f"🗑 حذف شد: {key}")
        else:
            bot.send_message(call.message.chat.id, "❌ پیدا نشد")


    # membership check
    elif call.data == "check_membership":
        if check_membership(call.from_user.id):
            first = list(movies.values())[0]
            send_media(call.message.chat.id, list(movies.keys())[0], first)
        else:
            bot.send_message(call.message.chat.id, "❌ عضو نیستی")


# ======================
# دریافت فایل
# ======================
@bot.message_handler(content_types=['video', 'photo', 'audio', 'document'])
def get_file(message):

    if not is_admin(message.from_user.id):
        return

    user_id = message.from_user.id

    if user_id not in waiting:
        return

    file_type = waiting[user_id]["type"]

    file_id = None

    if message.content_type == "video":
        file_id = message.video.file_id
    elif message.content_type == "photo":
        file_id = message.photo[-1].file_id
    elif message.content_type == "audio":
        file_id = message.audio.file_id
    elif message.content_type == "document":
        file_id = message.document.file_id

    key = f"{file_type}{len(movies)+1}"

    movies[key] = {
        "type": file_type,
        "file_id": file_id,
        "views": 0
    }

    waiting.pop(user_id)

    bot.send_message(message.chat.id, f"✅ ذخیره شد: {key}")


# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(message):

    if not check_membership(message.from_user.id):
        return bot.send_message(message.chat.id, "❌ اول عضو کانال شو")

    args = message.text.split()

    if len(args) > 1:
        key = args[1]

        item = movies.get(key)

        if item:
            send_media(message.chat.id, key, item)
        else:
            bot.send_message(message.chat.id, "❌ پیدا نشد")

    else:
        bot.send_message(message.chat.id, "👋 خوش آمدی")


bot.polling()
