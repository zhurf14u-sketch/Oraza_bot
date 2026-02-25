import asyncio
import aiohttp
import pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, TIMEZONE, CITY, COUNTRY, METHOD

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
scheduler = AsyncIOScheduler(timezone=pytz.timezone(TIMEZONE))

active_chats = set()


# ===== Получение времени намазов =====
async def get_prayer_times():
    url = (
        f"http://api.aladhan.com/v1/timingsByCity?"
        f"city={CITY}&country={COUNTRY}&method={METHOD}"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            timings = data["data"]["timings"]
            return timings["Fajr"], timings["Maghrib"]


# ===== Уведомления =====
async def send_suhur():
    for chat_id in active_chats:
        await bot.send_message(chat_id, "⏰ Время Fajr. Сухур завершён.")

async def send_iftar():
    for chat_id in active_chats:
        await bot.send_message(chat_id, "🌙 Время Maghrib. Можно разговляться.")


# ===== Обновление расписания =====
async def update_schedule():
    scheduler.remove_all_jobs()

    fajr, maghrib = await get_prayer_times()

    fajr_hour, fajr_min = map(int, fajr.split(":"))
    maghrib_hour, maghrib_min = map(int, maghrib.split(":"))

    scheduler.add_job(send_suhur, "cron", hour=fajr_hour, minute=fajr_min)
    scheduler.add_job(send_iftar, "cron", hour=maghrib_hour, minute=maghrib_min)

    # ежедневное автообновление
    scheduler.add_job(update_schedule, "cron", hour=0, minute=5)

    print("Расписание обновлено")


# ===== Команды =====
@router.message(Command("activate"))
async def activate(message: types.Message):
    active_chats.add(message.chat.id)
    await message.answer("✅ Напоминания активированы для этой группы.")

@router.message(Command("deactivate"))
async def deactivate(message: types.Message):
    active_chats.discard(message.chat.id)
    await message.answer("❌ Напоминания отключены.")

@router.message(Command("Danial"))
async def danial(message: types.Message):
    await message.answer("Даниал, ты лучший! Мой повелитель!")

@router.message(Command("Makhabat"))
async def makhabat(message: types.Message):
    await message.answer("Махабат, ты лучшая!")




dp.include_router(router)


# ===== Запуск =====
async def main():
    await update_schedule()
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())