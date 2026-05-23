import asyncio
import csv
import os
import sys
import pytz
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
print("Starting...", flush=True)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
KST = pytz.timezone("Asia/Seoul")

DAY_MAP = {
    "월요일": "mon",
    "화요일": "tue",
    "수요일": "wed",
    "목요일": "thu",
    "금요일": "fri",
    "토요일": "sat",
    "일요일": "sun",
}

CSV_PATH = os.path.join(os.path.dirname(__file__), "schedule.csv")


async def send_message(token: str, chat_id: str, text: str):
    async with Bot(token=token) as bot:
        await bot.send_message(chat_id=chat_id, text=text)
        print(f"[{asyncio.get_event_loop().time():.0f}] 전송 완료: {text[:30]}...")


def load_schedule(filepath: str):
    schedules = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["사용"].strip().upper() == "Y":
                schedules.append({
                    "day": row["요일"].strip(),
                    "time": row["시간"].strip(),
                    "message": row["메시지"].strip(),
                })
    return schedules


async def main():
    if not BOT_TOKEN:
        raise ValueError(".env 파일에 BOT_TOKEN이 없습니다.")
    if not CHAT_ID:
        raise ValueError(".env 파일에 CHAT_ID가 없습니다.")

    scheduler = AsyncIOScheduler(timezone=KST)
    schedules = load_schedule(CSV_PATH)

    for item in schedules:
        day = DAY_MAP[item["day"]]
        hour, minute = map(int, item["time"].split(":"))

        scheduler.add_job(
            send_message,
            CronTrigger(day_of_week=day, hour=hour, minute=minute, timezone=KST),
            args=[BOT_TOKEN, CHAT_ID, item["message"]],
            misfire_grace_time=60,
        )
        print(f"등록: {item['day']} {item['time']}")

    scheduler.start()
    print("봇 실행 중... (종료: Ctrl+C)")

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("봇 종료")
