import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# ==========================================
# КОНСТАНТИ И ПРАВИЛА ЗА ЗАЛОГ
# ==========================================
MIN_PERCENTAGE = 70  # поне 70% от общите пари
MIN_ODDS = 1.5       # поне 1.5 коефициент

def check_bet_conditions(option_volume, total_volume, odds):
    """Проверява дали залогът отговаря на условията за процент и коефициент."""
    if total_volume > 0:
        percentage = (option_volume / total_volume) * 100
    else:
        percentage = 0
        
    if percentage >= MIN_PERCENTAGE and odds >= MIN_ODDS:
        return True, percentage
    return False, percentage


# ==========================================
# ТЕЛЕГРАМ КОМАНДИ
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отговаря при въвеждане на /start"""
    await update.message.reply_text("Здравей! Ботът е активен и следи за залози по твоето правило (70% / 1.5).")


# ==========================================
# ФОНОВА ЗАДАЧА ЗА СЛЕДЕНЕ НА BETWATCH / ДАННИ
# ==========================================
async def monitor_bets(application):
    """
    Тук в бъдеще ще се върже заявката към Betwatch.
    В момента е подготвена структурата, която периодично проверява за нови данни.
    """
    while True:
        try:
            # === ТУК ЩЕ СЕ ВЗИМАТ ДАННИТЕ ОТ BETWATCH ===
            # Примерен симулиран залог (когато подкараш реалното API, ще го замениш тук):
            match_name = "Примерен мач"
            option_name = "Домакин да спечели"
            option_volume = 7500  # Пари за тази опция
            total_volume = 10000  # Общо заложени пари на пазара
            odds = 1.70           # Коефициент
            
            # Проверяваме през нашата функция
            is_valid, percentage = check_bet_conditions(option_volume, total_volume, odds)
            
            if is_valid:
                # Тук взимаш твоя Telegram Chat ID от environment variables или го задаваш директно
                chat_id = os.getenv("TELEGRAM_CHAT_ID")
                
                if chat_id:
                    message = (
                        f"🚨 **НАМЕРЕН СЪВПАДАЩ ЗАЛОГ!** 🚨\n\n"
                        f"⚽ Събитие: {match_name}\n"
                        f"🎯 Опция: {option_name}\n"
                        f"💰 Концентрация: {percentage:.1f}% (над 70% изискване)\n"
                        f"📊 Коефициент: {odds}"
                    )
                    await application.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Грешка при проверката на залозите: {e}")
            
        # Проверява на всеки 60 секунди (може да го промениш по желание)
        await asyncio.sleep(60)


async def post_init(application):
    """Стартира фоновата задача веднага след като ботът заработи."""
    asyncio.create_task(monitor_bets(application))


# ==========================================
# ОСНОВНА ФУНКЦИЯ
# ==========================================
def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    
    if not TOKEN:
        print("Грешка: Липсва TELEGRAM_TOKEN в променливите на средата!")
        return

    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()
    
    # Добавяме командата /start
    app.add_handler(CommandHandler("start", start))
    
    print("Ботът стартира...")
    app.run_polling()

if __name__ == "__main__":
    main()
