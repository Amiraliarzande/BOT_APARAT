import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot("7838816845:AAH22q3Ku9X_mzm6diFmgBYxbAhEERpOmIY")

CHANNEL_ID = "-1002898168031"
CHANNEL_LINK = "https://t.me/botaparat"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not check_subscribe(message):
        return
    bot.send_message(
        message.chat.id,
        "سلام به ربات دانلود از آپارات خوش آمدید!",
    )
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("🎥 ادامه (دانلود از آپارات)", callback_data="continue")
    btn2 = InlineKeyboardButton("💬 ارتباط با پشتیبان", callback_data="support")
    markup.add(btn1)
    markup.add(btn2)
    bot.send_message(message.chat.id, "لطفا یکی از گزینه‌ها را انتخاب کنید:", reply_markup=markup)

def check_subscribe(message):
    try:
        user_info = bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if user_info.status not in ['member', 'administrator', 'creator']:
            bot.send_message(
                message.chat.id,
                f"برای استفاده از ربات ابتدا باید عضو کانال ما شوید:\n[عضویت در کانال]({CHANNEL_LINK})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            return False
        return True
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ خطا در بررسی عضویت. لطفاً بعداً دوباره تلاش کنید."
        )
        print("Subscription check error:", e)
        return False

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "continue":
        bot.send_message(call.message.chat.id, "لطفا لینک ویدیو آپارات را ارسال کنید.")
    elif call.data == "support":
        bot.send_message(call.message.chat.id, "برای ارتباط با پشتیبانی کلیک کنید:\n👉 https://t.me/AmirRezaATT")

bot.infinity_polling()