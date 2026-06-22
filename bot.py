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
# منوی ادمین (دکمه‌ای)
# ======================
def admin_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("➕ Add Media", callback_data="add_media"),
        types.InlineKeyboardButton("🗑 Delete Media", callback_data="del_media")
    )
    markup.add(
        types.InlineKeyboardButton("📋 List Media", callback_data="list_media")
    )
    return markup


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
# ارسال فایل
# ======================
def send_media(chat_id, item):

    if not item:
        bot.send_message(chat_id, "❌ فایل پیدا نشد")
        return

    t = item["type"]
    f = item["file_id"]

    if t == "video":
        bot.send_video(chat_id, f)
    elif t == "photo":
        bot.send_photo(chat_id, f)
    elif t == "audio":
        bot.send_audio(chat_id, f)
    elif t == "document":
        bot.send_document(chat_id, f)
    else:
        bot.send_message(chat_id, "❌ نوع فایل ناشناخته")


# ======================
# حافظه موقت برای پنل ادمین
# ======================
pending = {}  # user_id -> action


# ======================
# گرفتن فایل از ادمین (برای اضافه کردن)
# ======================
@bot.message_handler(content_types=['video', 'photo', 'audio', 'document'])
def get_file(message):

    if not is_admin(message.from_user.id):
        return

    user_id = message.from_user.id

    if user_id not in pending:
        return

    action = pending[user_id]

    file_id = None
    file_type = None

    if message.content_type == 'video':
        file_id = message.video.file_id
        file_type = "video"

    elif message.content_type == 'photo':
        file_id = message.photo[-1].file_id
        file_type = "photo"

    elif message.content_type == 'audio':
        file_id = message.audio.file_id
        file_type = "audio"

    elif message.content_type == 'document':
        file_id = message.document.file_id
        file_type = "document"

    # ذخیره در movies (موقت)
    key = f"{file_type}_{len(movies)+1}"
    movies[key] = {
        "type": file_type,
        "file_id": file_id
    }

    pending.pop(user_id)

    bot.send_message(
        message.chat.id,
        f"✅ اضافه شد!\n\nkey: {key}\ntype: {file_type}"
    )


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
        "🧑‍💼 پنل ادمین",
        reply_markup=admin_markup()
    )


# ======================
# Callback های پنل
# ======================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    # start panel
    if call.data == "add_media":
        pending[call.from_user.id] = "add"
        bot.send_message(call.message.chat.id, "📥 حالا فایل (ویدیو/عکس/صدا) بفرست")

    elif call.data == "del_media":
        bot.send_message(call.message.chat.id, "❌ برای حذف: کلید فیلم را بفرست (مثلا film1)")
        pending[call.from_user.id] = "delete"

    elif call.data == "list_media":
        txt = "\n".join(movies.keys())
        bot.send_message(call.message.chat.id, f"📋 لیست:\n\n{txt}")

    elif call.data == "check_membership":

        if check_membership(call.from_user.id):
            bot.send_message(call.message.chat.id, "🎬 تایید شد!")
            first_item = list(movies.values())[0]
            send_media(call.message.chat.id, first_item)
        else:
            bot.send_message(call.message.chat.id, "❌ عضو نیستی", reply_markup=join_markup())


# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(message):

    args = message.text.split()

    if len(args) > 1:

        media_id = args[1]

        if not check_membership(message.from_user.id):
            bot.send_message(message.chat.id, "🎀 اول عضو شو", reply_markup=join_markup())
            return

        item = movies.get(media_id)

        if not item:
            bot.send_message(message.chat.id, "❌ پیدا نشد")
            return

        send_media(message.chat.id, item)

    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎬 دریافت", callback_data="go"))

        bot.send_message(message.chat.id, "👋 خوش آمدی", reply_markup=markup)


bot.polling()
