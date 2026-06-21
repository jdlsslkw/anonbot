import telebot
import os

TOKEN = os.getenv("TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(TOKEN)

# يخزن message_id -> user_id
replies = {}


@bot.message_handler(commands=['start'])
def start(message):

    if message.from_user.id == OWNER_ID:
        bot.reply_to(message, "أنت صاحب البوت.")
        return

    bot.reply_to(
        message,
        "📨 أرسل رسالتك بشكل مجهول."
    )


# استقبال الرسائل من المستخدمين
@bot.message_handler(
    func=lambda m: m.from_user.id != OWNER_ID,
    content_types=['text']
)
def receive(message):

    sent = bot.send_message(
        OWNER_ID,
        f"📨 الرسالة:\n\n{message.text}"
    )

    replies[sent.message_id] = message.from_user.id

    bot.reply_to(
        message,
        "✅ تم إرسال رسالتك."
    )


# رد صاحب البوت عن طريق Reply
@bot.message_handler(
    func=lambda m:
    m.from_user.id == OWNER_ID and
    m.reply_to_message is not None
)
def owner_reply(message):

    original_message_id = message.reply_to_message.message_id

    if original_message_id not in replies:

        bot.reply_to(
            message,
            "❌ هذه الرسالة ليست رسالة مجهولة."
        )

        return

    user_id = replies[original_message_id]

    bot.send_message(
        user_id,
        f"📩 الرد:\n\n{message.text}"
    )

    bot.reply_to(
        message,
        "✅ تم إرسال الرد."
    )


print("Bot Started...")

bot.infinity_polling()
