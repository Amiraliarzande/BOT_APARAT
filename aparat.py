import telebot
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests as RQ
import os
import re

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot("7838816845:AAH22q3Ku9X_mzm6diFmgBYxbAhEERpOmIY")


user_waiting_for_link = {}

if not os.path.exists("downloads"):
    os.makedirs("downloads")

def download_file(url, filename):
    response = RQ.get(url, stream=True)
    if response.status_code == 200:
        path = os.path.join("downloads", filename)
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
        return path
    else:
        raise Exception(f'Failed to retrieve video: status code {response.status_code}')

def extract_video_id(aparat_url):
    pattern = r"aparat\.com/v/([a-zA-Z0-9]+)"
    match = re.search(pattern, aparat_url)
    if match:
        return match.group(1)
    else:
        raise Exception("لینک آپارات معتبر نیست.")

def fetch_aparat_video(aparat_url):
    video_id = extract_video_id(aparat_url)
    api_url = f'https://www.aparat.com/api/fa/v1/video/video/show/videohash/{video_id}'
    resp = RQ.get(api_url)
    
    if resp.status_code != 200:
        raise Exception("خطا در دریافت اطلاعات از آپارات")

    json_data = resp.json()
    title = json_data['data']["attributes"]["title"]
    sources = json_data['data']["attributes"]["file_link_all"]

    for item in sources:
        if item['profile'] in ['720p', '480p', '360p']:  # کیفیت مطلوب
            urls_list = item.get('urls')
            for url in urls_list:
                filename = f"{video_id}_{item['profile']}.mp4"
                file_path = download_file(url, filename)
                return file_path, title

    raise Exception("هیچ لینک دانلودی با کیفیت مناسب پیدا نشد.")

CHANNEL_ID = "-1002898168031"
CHANNEL_LINK = "https://t.me/botaparat"


@bot.message_handler(commands=['support'])
def send_support(message):
    bot.send_message(message.chat.id, "برای ارتباط با پشتیبانی کلیک کنید:\n👉 https://t.me/AmirRezaATT")

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
        user_waiting_for_link[call.from_user.id] = True
        bot.send_message(call.message.chat.id, "✅ لطفاً لینک ویدیو آپارات را ارسال کنید.")
    elif call.data == "support":
        bot.send_message(call.message.chat.id, "برای ارتباط با پشتیبانی کلیک کنید:\n👉 https://t.me/AmirRezaATT")


@bot.message_handler(func=lambda message: True)
def handle_link(message):
    user_id = message.from_user.id
    if user_waiting_for_link.get(user_id):
        user_waiting_for_link[user_id] = False  # فقط یک بار اجازه بده

        aparat_url = message.text.strip()
        bot.send_message(message.chat.id, "⏳ در حال پردازش لینک و دانلود ویدیو...")

        try:
            file_path, title = fetch_aparat_video(aparat_url)
            with open(file_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption=title)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ خطایی رخ داد:\n{e}")
    




bot.infinity_polling()