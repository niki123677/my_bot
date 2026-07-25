import time
import requests

TELEGRAM_BOT_TOKEN = "8903055363:AAFBMAxrMhLAgkCylg0FY2SHmTeTv58NTqE"
TELEGRAM_CHAT_ID = "8386154079"

MIN_ODDS = 1.50
MIN_VOLUME_PERCENT = 80.0

sent_notifications = set()


def send_telegram_alert(event_name, selection, odds, volume_pct, total_staked):
    message = (
        f"🚨 *ОТКРИТ СТОЙНОСТЕН ЗАЛОГ!*\n\n"
        f"⚽ *Събитие:* {event_name}\n"
        f"🎯 *Селекция:* {selection}\n"
        f"📈 *Коефициент:* {odds}\n"
        f"📊 *Дял от парите:* {volume_pct:.1f}%\n"
        f"💰 *Общо заложени:* ${total_staked:,.2f}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"[+] Успешно изпратено известие за: {event_name}")
        else:
            print(f"[-] Грешка при изпращане: {response.text}")
    except Exception as e:
        print(f"[-] Грешка във връзката с Telegram: {e}")


def get_match_data():
    return [
        {
            "id": "match_1",
            "event_name": "Реал Мадрид vs Барселона",
            "selection": "Реал Мадрид",
            "odds": 1.75,
            "total_staked": 50000,
            "selection_staked": 42500,
        },
        {
            "id": "match_2",
            "event_name": "Арсенал vs Челси",
            "selection": "Арсенал",
            "odds": 1.35,
            "total_staked": 30000,
            "selection_staked": 27000,
        },
    ]


def run_monitor():
    print("🚀 Мониторингът е стартиран...")
    while True:
        try:
            matches = get_match_data()

            for match in matches:
                match_id = match["id"]
                total = match["total_staked"]
                staked = match["selection_staked"]
                odds = match["odds"]

                volume_pct = (staked / total * 100) if total > 0 else 0

                if odds >= MIN_ODDS and volume_pct >= MIN_VOLUME_PERCENT:
                    if match_id not in sent_notifications:
                        send_telegram_alert(
                            match["event_name"],
                            match["selection"],
                            odds,
                            volume_pct,
                            total,
                        )
                        sent_notifications.add(match_id)

        except Exception as e:
            print(f"Грешка: {e}")

        time.sleep(60)


if __name__ == "__main__":
    run_monitor()
