import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# ==========================================
# КОНСТАНТИ И ПРАВИЛА ЗА ЗАЛОГ
# ==========================================
MIN_PERCENTAGE = 70  # поне 70% от общите пари
MIN_ODDS = 1.5       # поне 1.5 коефициент

# Списък, в който пазим вече изпратените мачове, за да не се повтарят
sent_matches = set()

def check_bet_conditions(option_volume, total_volume, odds):
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
    await update.message.reply_text("Здравей! Ботът е активен и следи за залози по твоето правило (70% / 1.5). Всеки мач ще бъде пратен само веднъж.")


# ==========================================
# ФОНОВА ЗАДАЧА ЗА СЛЕДЕНЕ НА ДАННИТЕ
# ==========================================
async def monitor_bets(application):
    while True:
        try:
            # === ТУК СМЕНЯШ ИМЕТО НА МАЧА (или го връзваш с данните от Betwatch) ===
            match_name = "Реал Мадрид - Барселона"  
            option_name = "Победител 1"
            option_volume = 7500  
            total_volume = 10000  
            odds = 1.70           
            
            # Проверяваме дали този мач вече е бил изпращан
            if match_name in sent_matches:
                # Ако вече е пращан, го пропускаме и минаваме на следващата проверка
                await asyncio.sleep(60)
                continue

            is_valid, percentage = check_bet_conditions(option_volume, total_volume, odds)
            
            if is_valid:
                chat_id = os.getenv("TELEGRAM_CHAT_ID")
                
                if chat_id:
                    message = (
                        f"🚨 **НАМЕРЕН СЪВПАДАЩ ЗАЛОГ!** 🚨\n\n"
                        f"⚽ Мач: **{match_name}**\n"
                        f"🎯 Опция: {option_name}\n"
                        f"💰 Концентрация: {percentage:.1f}% (над 70% изискване)\n"
                        f"📊 Коефициент: {odds}"
                    )
                    await application.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
                    
                    # Добавяме мача в списъка с пратените, за да не се повтаря повече
                    sent_matches.add(match_name)
            
        except Exception as e:
            print(f"Грешка при проверката на залозите: {e}")
            
        await asyncio.sleep(60)


async def post_init(application):
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
    app.add_handler(CommandHandler("start", start))
    
    print("Ботът стартира...")
    app.run_polling()

if __name__ == "__main__":
    main()
