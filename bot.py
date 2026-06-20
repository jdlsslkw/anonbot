# Anonymous Telegram Bot
# الميزات:
# - رسائل مجهولة
# - رد بزر Reply
# - يدعم النصوص والصور والفيديو والملفات
# - يخزن المحادثات بقاعدة بيانات SQLite
#
# تثبيت:
# pip install pyTelegramBotAPI

import telebot
from telebot import types
import sqlite3

import os

import os

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(TOKEN)

db = sqlite3.connect("anon.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    anon_id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE
)
""")

db.commit()


def get_or_create(user_id):

    cur.execute(
        "SELECT anon_id FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        "SELECT MAX(anon_id) FROM users"
    )

    last = cur.fetchone()[0]

    anon_id = 100 if last is None else last + 1

    cur.execute(
        "INSERT INTO users VALUES (?,?)",
        (anon_id, user_id)
    )

    db.commit()

    return anon_id


def get_user(anon_id):

    cur.execute(
        "SELECT user_id FROM users WHERE anon_id=?",
        (anon_id,)
    )

    row = cur.fetchone()

    return row[0] if row else None


@bot.message_handler(commands=['start'])
def start(msg):

    get_or_create(msg.from_user.id)

    bot.reply_to(
        msg,
        "📨 أرسل رسالتك بشكل مجهول."
    )


# استقبال كل الرسائل من المستخدمين
@bot.message_handler(
    content_types=[
        'text',
        'photo',
        'video',
        'document'
    ]
)
def receive(msg):

    if msg.from_user.id == OWNER_ID:
        return

    anon_id = get_or_create(msg.from_user.id)

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            f"Reply #{anon_id}",
            callback_data=f"reply:{anon_id}"
        )
    )

    caption = f"📨 رسالة مجهولة\n\n#{anon_id}"

    if msg.content_type == 'text':

        bot.send_message(
            OWNER_ID,
            f"{caption}\n\n{msg.text}",
            reply_markup=kb
        )

    elif msg.content_type == 'photo':

        bot.send_photo(
            OWNER_ID,
            msg.photo[-1].file_id,
            caption=caption,
            reply_markup=kb
        )

    elif msg.content_type == 'video':

        bot.send_video(
            OWNER_ID,
            msg.video.file_id,
            caption=caption,
            reply_markup=kb
        )

    elif msg.content_type == 'document':

        bot.send_document(
            OWNER_ID,
            msg.document.file_id,
            caption=caption,
            reply_markup=kb
        )

    bot.reply_to(
        msg,
        "✅ تم إرسال رسالتك."
    )


# زر الرد
reply_wait = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("reply:"))
def callback(c):

    if c.from_user.id != OWNER_ID:
        return

    anon_id = int(c.data.split(":")[1])

    reply_wait[c.from_user.id] = anon_id

    bot.send_message(
        OWNER_ID,
        f"✏️ اكتب الرد للمستخدم #{anon_id}"
    )


# إرسال الرد
@bot.message_handler(
    func=lambda m: (
        m.from_user.id == OWNER_ID and
        m.from_user.id in reply_wait
    )
)
def send_reply(msg):

    anon_id = reply_wait[msg.from_user.id]

    user_id = get_user(anon_id)

    if user_id:

        bot.send_message(
            user_id,
            f"📩 رد جديد:\n\n{msg.text}"
        )

        bot.reply_to(
            msg,
            "✅ تم إرسال الرد."
        )

    del reply_wait[msg.from_user.id]


print("Bot Started...")
bot.infinity_polling()
