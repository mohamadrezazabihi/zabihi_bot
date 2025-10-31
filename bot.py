import asyncio
from telethon import TelegramClient, events
import re
import logging
import jdatetime
import os
from dotenv import load_dotenv

load_dotenv()
# =======================
# تنظیمات لاگ
# =======================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =======================
# اطلاعات API تلگرام
# =======================
api_id = int(os.environ.get("API_ID", "0"))
api_hash = os.environ.get("API_HASH", "")
phone_number = os.environ.get("PHONE_NUMBER", "")

# =======================
# کانال‌ها
# =======================
source_channel = 'bazartalair'
target_channel = 'jewelry_zabihi'

# =======================
# ذخیره آخرین قیمت‌ها برای مقایسه
# =======================
last_prices = {}

# =======================
# فرمول طلای 18 عیار
# =======================
GOLD_18_RATIO = 4.3318

# =======================
# توابع کمکی
# =======================
def get_trend_emoji(current_price, last_price):
    if last_price is None:
        return "🔸"
    if current_price > last_price:
        return "🔼"
    elif current_price < last_price:
        return "🔽"
    else:
        return "➡️"

def extract_all_prices(text):
    if not text:
        return None
    prices = {}
    patterns = {
        'abshodeh': r'آبشده نقد فردا\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_emam_86': r'سکه 86\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_nim_86': r'نیم سکه 86\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_rob_86': r'ربع سکه 86\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_emam_tarikh_paeen': r'سکه تمام تاریخ پایین\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_nim_tarikh_paeen': r'نیم سکه تاریخ پایین\s*\n.*?فروش:\s*([\d,]+)',
        'sekke_rob_tarikh_paeen': r'ربع سکه تاریخ پایین\s*\n.*?فروش:\s*([\d,]+)',
        'ons_global': r'انس طلا\s*:\s*([\d.,]+)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).replace(',', '').replace(' ', '')
            try:
                prices[key] = float(value) if key == 'ons_global' else int(value)
            except:
                prices[key] = None
        else:
            prices[key] = None
    return prices

def calculate_18k_gold_price(abshodeh_price):
    if not abshodeh_price:
        return 0
    return int(round(abshodeh_price / GOLD_18_RATIO))

def create_persian_date():
    return jdatetime.datetime.now().strftime("%Y/%m/%d")

def format_price(price):
    if price is None or price == 0:
        return "---"
    if isinstance(price, float):
        return f"{price:.2f}"
    return f"{price:,}"

def create_complete_message(prices):
    persian_date = create_persian_date()
    gold_18_price = calculate_18k_gold_price(prices.get('abshodeh'))
    trends = {k: get_trend_emoji(v, last_prices.get(k)) for k, v in prices.items()}
    gold_18_trend = get_trend_emoji(prices.get('abshodeh'), last_prices.get('abshodeh'))
    
    message = f"""⚜️طلا و سکه ذبیحی⚜️

📅امروز {persian_date}

{trends.get('abshodeh', '🔸')} آبشده نقدی
🟡فروش : {format_price(prices.get('abshodeh'))}

{gold_18_trend} طلا 18
🟠فروش گرم : {format_price(gold_18_price)}

{trends.get('sekke_emam_86', '🔸')} سکه امام 86
🌕فروش : {format_price(prices.get('sekke_emam_86'))}

{trends.get('sekke_nim_86', '🔸')} سکه نیم 86
🌓فروش : {format_price(prices.get('sekke_nim_86'))}

{trends.get('sekke_rob_86', '🔸')} سکه ربع 86
🌒فروش : {format_price(prices.get('sekke_rob_86'))}

{trends.get('sekke_emam_tarikh_paeen', '🔸')} سکه امام تاریخ پایین 
🌕فروش : {format_price(prices.get('sekke_emam_tarikh_paeen'))}

{trends.get('sekke_nim_tarikh_paeen', '🔸')} سکه نیم تاریخ پایین 
🌓فروش : {format_price(prices.get('sekke_nim_tarikh_paeen'))}

{trends.get('sekke_rob_tarikh_paeen', '🔸')} سکه ربع تاریخ پایین 
🌒فروش : {format_price(prices.get('sekke_rob_tarikh_paeen'))}

{trends.get('ons_global', '🔸')} انس جهانی طلا : {format_price(prices.get('ons_global'))}

📞09155112399
📞09220309946
📞09205210017
📌کانال تلگرام : @jewelry_zabihi"""
    
    return message

# =======================
# هندلر پیام
# =======================
async def message_handler(event):
    message_text = event.message.text
    prices = extract_all_prices(message_text)
    if prices and prices.get('abshodeh'):
        complete_message = create_complete_message(prices)
        await client.send_message(target_channel, complete_message)
        for k, v in prices.items():
            if v is not None:
                last_prices[k] = v

# =======================
# اجرای ربات
# =======================
async def main():
    global client
    client = TelegramClient('gold_price_session', api_id, api_hash)
    await client.start(phone=phone_number)
    client.add_event_handler(message_handler, events.NewMessage(chats=source_channel))
    logger.info("🟢 ربات شروع به کار کرد و در حال گوش دادن به پیام‌ها...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
