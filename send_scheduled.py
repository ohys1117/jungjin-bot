import asyncio
import csv
import os
from datetime import datetime
import pytz
from telegram import Bot

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
KST = pytz.timezone("Asia/Seoul")

DAY_NAMES = {0: "월요일", 1: "화요일", 2: "수요일", 3: "목요일", 4: "금요일", 5: "토요일", 6: "일요일"}


async def main():
    now = datetime.now(KST)
    day = DAY_NAMES[now.weekday()]
    now_minutes = now.hour * 60 + now.minute

    messages = []
    with open("schedule.csv", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row["사용"].strip().upper() != "Y":
                continue
            if row["요일"].strip() != day:
                continue
            h, m = map(int, row["시간"].strip().split(":"))
            if abs(now_minutes - (h * 60 + m)) <= 15:
                messages.append(row["메시지"].strip())

    if not messages:
        print(f"전송할 메시지 없음: {day} {now.strftime('%H:%M')}")
        return

    async with Bot(token=BOT_TOKEN) as bot:
        for msg in messages:
            await bot.send_message(chat_id=CHAT_ID, text=msg)
            print(f"전송 완료: {msg[:30]}...")


asyncio.run(main())
