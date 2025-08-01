from sqlalchemy.dialects.mysql import insert
from sqlalchemy import update, select
from SQLAlchemy import User, Income, Expense, UserCategory
from SQLAlchemy import Saving
import datetime


async def save_name_to_db(user_id, user_name, database):
    result = await database.execute(update(User).filter(User.id == user_id).values(name = user_name))
    if result.rowcount == 0:
        await database.execute(insert(User).values(id = user_id, name = user_name))
    await database.commit()
    return f"Приятно познакомиться, '{user_name}'!"


async def save_income_to_db(category, user_id, amount, date, is_fixed, database):
    result = await database.execute(select(UserCategory.id).filter(UserCategory.user_id == user_id, UserCategory.name == category))
    category_id = result.scalar_one_or_none()
    if not category_id:
        result = await database.execute(insert(UserCategory).values(user_id = user_id, name = category))
        category_id = result.inserted_primary_key[0]  #мы берем айди новой категории
    await database.execute(insert(Income).values(category_id = category_id, user_id = user_id, amount = amount, date = date, is_fixed = is_fixed))
    await database.commit()
    return f"Доход успешно добавлен"


async def save_expense_to_db(category, user_id, amount, date, is_fixed, database):
    result = await database.execute(select(UserCategory.id).filter(UserCategory.user_id == user_id, UserCategory.name == category))
    category_id = result.scalar_one_or_none()
    if not category_id:
        result = await database.execute(insert(UserCategory).values(user_id = user_id, name = category))
        category_id = result.inserted_primary_key[0]  #мы берем айди новой категории
    await database.execute(insert(Expense).values(category_id = category_id, user_id = user_id, amount = amount, date = date, is_fixed = is_fixed))
    await database.commit()
    return f"Расход успешно добавлен"


async def save_saving_to_db(user_id, amount, date, database):
    await database.execute(insert(Saving).values(user_id = user_id, amount = amount, date = date))
    await database.commit()
    return f"Накопление успешно добавлено"


async def get_balance_from_db(user_id, database):
    incomes = await database.execute(select(Income.amount).filter(Income.user_id == user_id))
    sum_incomes = sum(income[0] for income in incomes.fetchall() if income[0] is not None)

    expenses = await database.execute(select(Expense.amount).filter(Expense.user_id == user_id))
    sum_expenses = sum(expense[0] for expense in expenses.fetchall() if expense[0] is not None)

    savings = await database.execute(select(Saving.amount).filter(Saving.user_id == user_id))
    sum_savings = sum(saving[0] for saving in savings.fetchall() if saving[0] is not None)

    balance = sum_incomes - (sum_expenses + sum_savings)

    return {
        'incomes': sum_incomes,
        'expenses': sum_expenses,
        'savings': sum_savings,
        'total': balance
    }


async def get_user_history_from_db(user_id, database):
    today = datetime.date.today()
    start_month = datetime.date(today.year, today.month, 1)
    incomes = await database.execute(select(Income.amount, Income.date, Income.is_fixed, UserCategory.name).join(UserCategory, UserCategory.id == Income.category_id).filter(Income.user_id == user_id, Income.date >= start_month))
    expenses = await database.execute(select(Expense.amount, Expense.date, Expense.is_fixed, UserCategory.name).join(UserCategory, UserCategory.id == Expense.category_id).filter(Expense.user_id == user_id, Expense.date >= start_month))
    savings = await database.execute(select(Saving.amount, Saving.date).filter(Saving.user_id == user_id, Saving.date >= start_month))
    return incomes, expenses, savings

# async def save_user_category_to_db(category_name, user_id, database):
#     result = await database.execute(select(UserCategory.id).filter(UserCategory.user_id == user_id, UserCategory.name == category_name))
#     if result.rowcount == 0:
#         result = await database.execute(insert(UserCategory).values(user_id = user_id, name = category_name))
#         category_id = result.inserted_primary_key[0]  #мы берем айди новой категории
#     await database.execute(insert(Saving).values(category_id = category_id, user_id = user_id, name = category_name))
#     await database.commit()
#     return f"Категория '{category_name}' успешно добавлена"