from datetime import datetime
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import StarTransaction, Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, \
    InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from DataBase import save_name_to_db, save_income_to_db, save_expense_to_db, save_saving_to_db, \
    get_balance_from_db, get_user_history_from_db
from SQLAlchemy import Base, User
from aiogram.filters import StateFilter

TOKEN = "8155567682:AAFhedmhBJIs4U8hWEtzf_xjRmidaA1hu1k"
DB_NAME = 'postgres'
DB_PORT = '5433'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = 'localhost'

bot = Bot(token = TOKEN)
dp = Dispatcher()

engine = create_async_engine(f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

@asynccontextmanager
async def get_db():
    async with AsyncSession(engine) as db:
        try:
            yield db
        finally:
           await db.close()

async def create_tables():
    async with engine.begin() as connection:
        #await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    print('таблицы созданы')

@dp.message(Command("start"))
async def start_handler(message:Message, state: FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    async with get_db() as db:
        user_in_db =  await db.get(User, user_id)
    if not user_in_db:
        await state.set_state(NameState.waiting_name)
        await message.answer(
            f"👋 Привет, {user_name}! Добро пожаловать в моего бота!\n\n"
            "Я рада видеть тебя здесь впервые!\n"
            "Напиши как ты хочешь, чтобы я тебя называла: "
        )
    else:
        await message.answer(f"Добро пожаловать в дневник бюджета, {user_in_db.name}!" , reply_markup = reply_keyboard())

@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ Справка по работе с ботом\n\n"
        "Все взаимодействие происходит через кнопки меню:\n\n"
        "🟢 Доход: запись новых поступлений денежных средств\n\n"
        "🔻 Расход:\n"
        "   • Запись новых трат\n"
        "   • Добавление своих категорий расходов\n"
        "   • Установка месячных лимитов по категориям\n"
        "   • Просмотр остатков лимитов\n\n"
        "💰 Накопления: учет сбережений и инвестиций\n\n"
        "📊 Баланс/История:\n"
        "   • Просмотр текущего баланса\n"
        "   • История всех операций за месяц\n\n"
        "Для начала работы просто нажмите нужную кнопку в меню!"
    )

class NameState(StatesGroup):
    waiting_name = State()
    waiting_rename = State()

@dp.message(Command("rename"))
async def rename_handler(message: Message, state: FSMContext):
    await state.set_state(NameState.waiting_rename)
    await message.answer("Введите ваше новое имя: ")

@dp.message(NameState.waiting_rename)
async def set_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text
    async with get_db() as db:
         await save_name_to_db(user_id, name, db)
    await message.answer("Ваше новое имя успешно сохранено!")
    await state.clear()

@dp.message(NameState.waiting_name)
async def set_name(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text
    async with get_db() as db:
         await save_name_to_db(user_id, name, db)
    await message.answer(
        "Твое имя успешно сохранено!\n"
        "Добро пожаловать в финансовый помощник! 🎉\n\n"
        "О боте 🤖\n"
        "Финансовый помощник — это персональный инструмент для управления финансами, созданный на основе моего авторского подхода к расчёту бюджета! Я разработала систему, которая помогает эффективно контролировать доходы и расходы, учитывая нюансы финансового планирования.\n\n"
        "Как это работает 💡\n"
        "Доходы — все поступления денежных средств\n"
        "Расходы — все траты\n"
        " Доходы и расходы разделяются на две группы:\n"
        "* Фиксированные — регулярные платежи/пополнения с предсказуемой суммой (аренда, коммунальные услуги, подписки, зарплата)\n"
        "* Нефиксированные — нерегулярные платежи/пополнения с переменной суммой (штрафы, развлечения, премии)\n\n"
        "🟢 Месячные лимиты устанавливаются для фиксированных расходов, что позволяет:\n"
        "* Точно планировать ежемесячные траты\n"
        "* Избегать перерасходов\n"
        "* Контролировать финансовое состояние\n\n"
        "🟢 Накопления\n"
        "Отдельная категория для накоплений, которая учитывается в общем бюджете как расход. Это помогает:\n"
        "* Формировать финансовую подушку\n"
        "* Планировать крупные покупки\n\n"
        "🟢 Ваши действия:\n"
        "* Добавляйте все доходы, расходы и накопления\n"
        "* Следите за лимитами по фиксированным расходам\n"
        "* Планируйте накопления как часть бюджета\n\n"
        "Начните использовать все возможности бота прямо сейчас!\n"
        "Если у вас возникнут вопросы, обращайтесь ко мне напрямую @Statrixxx\n"
        "Удачи в управлении финансами! 💼", reply_markup=reply_keyboard()
    )
    await state.clear()

class TransactionState(StatesGroup):
    waiting_category = State()
    waiting_amount = State()
    waiting_date = State()
    waiting_is_fixed = State()

class SavingState(StatesGroup):
    waiting_amount = State()
    waiting_date = State()

#Хэндлер для записи доходов и расходов
@dp.message(Command("add_income"))
@dp.message(Command("add_expense"))
@dp.message(F.text == "Доходы")
@dp.message(F.text == "Расходы")
async def add_transaction_handler(message: Message, state: FSMContext):
    # Определяем тип операции (доход/расход)
    if message.text in ["/add_income", "Доходы"]:
        transaction_type = "income"
    else:
        transaction_type = "expense"

    await state.set_state(TransactionState.waiting_category)
    await state.update_data(e_or_i=transaction_type)
    await message.answer("Введите категорию: ")


@dp.message(TransactionState.waiting_category)
async def set_category(message: Message, state: FSMContext):
    category = message.text.lower()
    await state.update_data(category=category)
    await state.set_state(TransactionState.waiting_amount)
    await message.answer("Введи сумму: ")


@dp.message(TransactionState.waiting_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await state.set_state(TransactionState.waiting_date)
        now = datetime.now()
        await message.answer(
            "Выберите дату: ",
            reply_markup=await SimpleCalendar().start_calendar(year=now.year, month=now.month)
        )
    except ValueError:
        await message.answer("Пожалуйста, введи корректную сумму (число):")


@dp.message(TransactionState.waiting_is_fixed)
async def save_transaction(message: Message, state: FSMContext):
    is_fixed_answer = message.text.lower()
    user_id = message.from_user.id
    is_fixed = is_fixed_answer == "да"

    data = await state.get_data()

    async with get_db() as db:
        if data['e_or_i'] == "income":
            await save_income_to_db(
                data['category'], user_id, data['amount'],
                data['date'], is_fixed, db
            )
            await message.answer("Доход успешно сохранен!", reply_markup=reply_keyboard())
        elif data['e_or_i'] == "expense":
            await save_expense_to_db(
                data['category'], user_id, data['amount'],
                data['date'], is_fixed, db
            )
            await message.answer("Расход успешно сохранен!", reply_markup=reply_keyboard())
        else:
            await message.answer("Ошибка")

    await state.clear()

#хэндлер для накоплений
@dp.message(Command("add_saving"))
@dp.message(F.text == "Накопления")
async def add_saving_handler(message: Message, state: FSMContext):
    await state.set_state(SavingState.waiting_amount)
    await message.answer("Введи сумму накопления: ")

@dp.message(SavingState.waiting_amount)
async def set_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Сумма не может быть <= 0")
            return
        await state.update_data(amount=amount)
        await state.set_state(SavingState.waiting_date)
        now = datetime.now()
        await message.answer(
            "Выбери дату: ",
            reply_markup=await SimpleCalendar().start_calendar(year=now.year, month=now.month)
        )
    except ValueError:
        await message.answer("Пожалуйста, введи корректную сумму (число):")

#дальше идет календарь

#Хэндлер для кнопки баланса
@dp.message(F.text == "Баланс/История")
async def get_balance_button_handler(message: Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Показать баланс",callback_data= "btn1"), InlineKeyboardButton(text="Показать историю",callback_data= "btn2")],])
    await message.answer("Нажми на кнопку", reply_markup= keyboard)


#Хэндлер для показа баланса
@dp.callback_query(F.data == "btn1")
async def get_balance_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup(reply_markup=None)
    async with get_db() as db:
        balance = await get_balance_from_db(user_id, db)
        await callback.answer("куку")
        await callback.message.answer(
            f"Ваш текущий баланс:\n\n"
            f"✅ Доходы: {balance['incomes']:,.2f} ₽\n"
            f"❌ Расходы: {balance['expenses']:,.2f} ₽\n"
            f"💵 Накопления: {balance['savings']:,.2f} ₽\n\n"
            f"🎯 Итоговый баланс: {balance['total']:,.2f} ₽\n\n"
            f"*Формула расчета:*\n"
            f"Баланс = Доходы - (Расходы + Накопления)"
        )

#Хэндлер для показа истории записей
@dp.callback_query(F.data == "btn2")
async def get_history_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    user_id = callback.from_user.id

    async with get_db() as db:
        incomes, expenses, savings = await get_user_history_from_db(user_id, db)

        if not any([incomes, expenses, savings]):
            await callback.message.answer("📊 История операций за текущий месяц пуста.")
            return

        response = [
            "📊 История операций с начала месяца:",
            "🔹 - фиксированный | 🔸 - нефиксированный\n"
        ]

        if incomes:
            response.append("\n💵 Доходы:")
            for amount, date, is_fixed, category in incomes:
                line = format_history_line(amount, date, is_fixed, category, "🟢")
                response.append(line)

        if expenses:
            response.append("\n🔻 Расходы:")
            for amount, date, is_fixed, category in expenses:
                line = format_history_line(amount, date, is_fixed, category, "🔴")
                response.append(line)

        if savings:
            response.append("\n💰 Накопления:")
            for amount, date in savings:
                date_str = date.strftime("%d.%m")
                amount_str = f"{float(amount):.2f}"
                response.append(f"🟣 {date_str} | {'Накопления':<15} | {amount_str:>8} руб.")


        full_message = "\n".join(response)
        if len(full_message) > 4000:  # Telegram имеет лимит на длину сообщения
            part1 = "\n".join(response[:len(response) // 2])
            part2 = "\n".join(response[len(response) // 2:])
            await callback.message.answer(part1)
            await callback.message.answer(part2)
        else:
            await callback.message.answer(full_message)

def format_history_line(amount, date, is_fixed, category, emoji):
    amount_str = f"{float(amount):.2f}"
    date_str = date.strftime("%d.%m")
    type_icon = "🔹" if is_fixed else "🔸"
    return f"{emoji} {type_icon} {date_str} | {category[:15]:<15} | {amount_str:>8} руб."


@dp.message(F.text & ~F.command)
async def handler_text(message: Message):
    await message.answer("Пожалуйста, воспользуйся кнопками или командами", reply_markup=reply_keyboard())

@dp.callback_query(SimpleCalendarCallback.filter())
async def set_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    user_id = callback_query.from_user.id
    result, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if result:
        await state.update_data(date=date)
        data = await state.get_data()
        if data.get('e_or_i') in ["income", "expense"]:
            await state.set_state(TransactionState.waiting_is_fixed)
            await callback_query.message.answer(
                "Это фиксированный доход/расход? (Да/Нет): ")
        else:
            async with get_db() as db:
                await save_saving_to_db(
                    user_id, data['amount'], data['date'], db)

            await state.clear()
            await callback_query.message.answer("Накопление успешно сохранено!")


@dp.message(F.text.in_(["Доходы", "Расходы", "Накопления", "Баланс/История"]), StateFilter('*'))
async def cancel_previous_state(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Предыдущее действие отменено")

    if message.text == "Доходы" or message.text == "Расходы":
        await add_transaction_handler(message, state)
    elif message.text == "Накопления":
        await add_saving_handler(message, state)
    elif message.text == "Баланс/История":
        await  get_balance_button_handler(message, state)

def reply_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Доходы"), KeyboardButton(text="Расходы")],
        [KeyboardButton(text="Накопления"), KeyboardButton(text="Баланс/История")]
    ], resize_keyboard=True)

async def run_bot():
    await create_tables()
    await dp.start_polling(bot)

asyncio.run(run_bot())