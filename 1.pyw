import logging
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

# Telegram bot token
TOKEN = "7788775278:AAHHqBXxRuuPRFv1Nb5ewRlWGKZmePdA87E"

# Bot va Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Tugmalar
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Strategiyani ko‘rsatish")],
        [KeyboardButton(text="Davom etish")],
        [KeyboardButton(text="To‘xtatish")]
    ],
    resize_keyboard=True
)

# **Strategiya holati**
class StrategyState(StatesGroup):
    active = State()

# **Konstantalar**
TOTAL_ROWS = 9
SAFE_UP_TO = 7  # 100% xavfsiz qatorlar
EIGHTH_ROW_PROB = 0.8  # 80% xavfsizlik
NINTH_ROW_PROB = 0.6  # 60% xavfsizlik

# **Chirik olma tarixi**
rotten_apples = {i: [] for i in range(1, TOTAL_ROWS + 1)}

# **Xavfsiz tugmalarni aniqlash**
def get_safe_positions(row):
    """Oldingi natijalarga asoslanib xavfsiz tugmalarni tanlaydi"""
    all_positions = [1, 2, 3, 4, 5]

    # Agar avval "chirik olma" chiqgan bo'lsa, uni olib tashlaymiz
    if row in rotten_apples and rotten_apples[row]:
        all_positions = [pos for pos in all_positions if pos not in rotten_apples[row]]

    return all_positions if all_positions else [1, 2, 3, 4, 5]  # Agar hammasi xavfli bo'lsa, tavakkal

# **Strategiyani hisoblash**
def calculate_strategy():
    """Chirik olmasiz optimal strategiyani ishlab chiqadi"""
    strategy = []

    # 1–7-qatorlar (100% xavfsiz)
    for row in range(1, SAFE_UP_TO + 1):
        safe_positions = get_safe_positions(row)
        choice = random.choice(safe_positions)
        strategy.append(choice)

    # 8-qator (80% xavfsizlik)
    safe_positions = get_safe_positions(8)
    if random.random() < EIGHTH_ROW_PROB:
        choice = random.choice(safe_positions)
    else:
        choice = random.choice([1, 2, 3, 4, 5])  # Tavakkal

    strategy.append(choice)

    # 9-qator (60% xavfsizlik)
    safe_positions = get_safe_positions(9)
    if random.random() < NINTH_ROW_PROB:
        choice = random.choice(safe_positions)
    else:
        choice = random.choice([1, 2, 3, 4, 5])  # Tavakkal

    strategy.append(choice)

    return strategy

# **Start komandasi**
@dp.message(lambda message: message.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Salom! Apple of Fortune uchun strategiyani ko‘rish uchun tugmalardan foydalaning.", reply_markup=keyboard)

# **Strategiyani ko‘rsatish**
@dp.message(lambda message: message.text == "Strategiyani ko‘rsatish")
async def show_strategy(message: types.Message, state: FSMContext):
    strategy = calculate_strategy()
    await state.update_data(strategy=strategy, step=0)
    await message.answer(f"1-qator uchun tanlangan tugma: {strategy[0]}")
    await state.set_state(StrategyState.active)

# **Davom etish**
@dp.message(lambda message: message.text == "Davom etish")
async def continue_strategy(message: types.Message, state: FSMContext):
    data = await state.get_data()
    strategy = data.get("strategy", [])
    step = data.get("step", 0)

    if step < len(strategy) - 1:
        step += 1
        await state.update_data(step=step)
        await message.answer(f"{step+1}-qator uchun tanlangan tugma: {strategy[step]}")
    else:
        await message.answer("Strategiya yakunlandi.")
        await state.clear()

# **To‘xtatish**
@dp.message(lambda message: message.text == "To‘xtatish")
async def stop_strategy(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Strategiya to‘xtatildi.")

# **Chirik olma joylashuvi**
@dp.message()
async def set_rotten_apple(message: types.Message):
    global rotten_apples
    if message.text.startswith("Oxirgi chirik olma:"):
        try:
            parts = message.text.split(":")[1].strip().split()
            row = int(parts[0])
            pos = int(parts[1])

            # Chirik olmani eslab qolamiz
            if row in rotten_apples:
                rotten_apples[row].append(pos)
            else:
                rotten_apples[row] = [pos]

            await message.answer(f"Chirik olma {row}-qator, {pos}-tugmada saqlandi. Keyingi strategiya shunga mos ravishda hisoblanadi.")
        except:
            await message.answer("Chirik olma formati noto‘g‘ri. Masalan: 'Oxirgi chirik olma: 3 2'")

# **Botni ishga tushirish**
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())