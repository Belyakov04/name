import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db, add_user, add_referral, get_user_level, update_score
from game import NumberGame
from utils import log_command
from achievements import check_achievements
from daily_rewards import init_rewards_db, get_reward
from quests import check_quests


# Настройка логгирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Глобальные переменные
user_games = {}  # Хранение игр пользователей


# ---- Клавиатуры ----
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎮 Играть", callback_data='game')],
        [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
        [InlineKeyboardButton("📢 Рефералка", callback_data='refer')]
    ]
    return InlineKeyboardMarkup(keyboard)


# ---- Команды ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    args = context.args

    # Реферальная система
    if args and args[0].startswith('ref_'):
        referrer_id = int(args[0][4:])
        add_referral(referrer_id, user_id)
        await update.message.reply_text("🎉 Ты зарегистрировался по реферальной ссылке!")

    add_user(user_id, username)  # Добавляем пользователя в БД
    await update.message.reply_text(
        "Привет! Я многофункциональный бот. Выбери действие:",
        reply_markup=main_menu()
    )
    log_command("start", user_id, username)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    📌 Доступные команды:
    /start - Начать работу
    /help - Помощь
    /game - Играть в игру
    /stats - Моя статистика
    /refer - Реферальная программа
    /profile - Мой уровень
    """
    await update.message.reply_text(help_text)
    log_command("help", update.effective_user.id, update.effective_user.username)


# ---- Игра ----
async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_games[user_id] = NumberGame()
    await update.callback_query.message.reply_text("🔢 Я загадал число от 1 до 100. Угадывай!")


async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_games:
        await update.message.reply_text("Сначала начни игру через /game")
        return

    try:
        guess_num = int(context.args[0])
        game = user_games[user_id]
        result = game.check_guess(guess_num)

        if "угадал" in result:
            update_score(user_id, 10)
            del user_games[user_id]  # Удаляем завершенную игру

        await update.message.reply_text(result)
    except (IndexError, ValueError):
        await update.message.reply_text("Используй: /guess <число>")


async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    achievements_list = check_achievements(user_id)
    if achievements_list:
        text = "🏆 Ваши достижения:\n• " + "\n• ".join(achievements_list)
    else:
        text = "У вас пока нет достижений. Продолжайте играть!"
    await update.message.reply_text(text)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    reward = get_reward(user_id)
    if reward > 0:
        update_score(user_id, reward)
        await update.message.reply_text(
            f"🎁 Вы получили {reward} очков за ежедневную награду!\n"
            f"Возвращайся завтра за большей наградой!"
        )
    else:
        await update.message.reply_text("Вы уже получали награду сегодня")


async def quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_stats = {
        'games_played': 5,  # Здесь должна быть реальная статистика
        'total_score': get_user_score(user_id)
    }
    completed = check_quests(user_stats)
    if completed:
        text = "✅ Выполненные квесты:\n"
        for title, reward in completed:
            text += f"• {title} (+{reward} очков)\n"
    else:
        text = "У вас нет выполненных квестов"
    await update.message.reply_text(text)


# ---- Профиль ----
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        await update.message.reply_text(f"🏆 Твой счет: {result[0]} очков")
    else:
        await update.message.reply_text("Ты еще не играл!")


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    level = get_user_level(user_id)
    await update.message.reply_text(f"✨ Твой уровень: {level}\nКаждые 100 очков = 1 уровень")


# ---- Рефералы ----
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    await update.message.reply_text(


    f"Приглашай друзей и получай бонусы!\n"
    f"Твоя ссылка: https://t.me/{bot_username}?start=ref_{user_id}"
    )

    # ---- Чат ----
    async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
        responses = {
            "привет": "Привет! 😊",
            "как дела": "Отлично! Как сам?",
            "пока": "До скорой встречи! 👋"
        }
        user_text = update.message.text.lower()
        reply = responses.get(user_text, "Я не понял... Напиши /help")
        await update.message.reply_text(reply)

    # ---- Админка ----
    async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in ADMIN_IDS:
            await update.message.reply_text("❌ Доступ запрещен!")
            return

        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        conn.close()
        await update.message.reply_text(f"👥 Всего пользователей: {count}")

    # ---- Обработчики ----
    async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data == 'game':
            await game_callback(update, context)
        elif query.data == 'stats':
            await stats(update, context)
        elif query.data == 'refer':
            await refer(update, context)

    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Ошибка: {context.error}")
        if update.effective_message:
            await update.effective_message.reply_text("⚠️ Произошла ошибка!")

    # ---- Запуск ----
    def main():
        init_db()  # Инициализация БД
        init_rewards_db()
        application.add_handler(CommandHandler("daily", daily))
        app = Application.builder().token(BOT_TOKEN).build()


        # Команды
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help))
        app.add_handler(CommandHandler("game", game_callback))
        app.add_handler(CommandHandler("guess", guess))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CommandHandler("profile", profile))
        app.add_handler(CommandHandler("refer", refer))
        app.add_handler(CommandHandler("admin", admin_stats))



        # Кнопки
        app.add_handler(CallbackQueryHandler(button_click))

        application.add_handler(CommandHandler("quests", quests))

        application.add_handler(CommandHandler("achievements", achievements))

        # Чат
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))


        # Ошибки
        app.add_error_handler(error_handler)

        app.run_polling()

    if name == "__main__":
        main()
