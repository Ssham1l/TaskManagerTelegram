import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

# Включаем логирование для отладки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
NAME, EMAIL = range(2)

# "База данных" для регистрации пользователей (для демонстрации используем словарь)
registered_users = {}

def start(update: Update, context: CallbackContext) -> int:
    """Обработка команды /start. Проверяем, зарегистрирован ли пользователь."""
    user = update.message.from_user
    if user.id in registered_users:
        update.message.reply_text(
            f"Привет, {registered_users[user.id]['name']}! Ты уже зарегистрирован."
        )
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Добро пожаловать! Давай зарегистрируемся. Как тебя зовут?"
        )
        return NAME

def name_handler(update: Update, context: CallbackContext) -> int:
    """Получаем имя пользователя и запрашиваем email."""
    user = update.message.from_user
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text(
        f"Отлично, {name}! Теперь введи свою электронную почту."
    )
    return EMAIL

def email_handler(update: Update, context: CallbackContext) -> int:
    """Получаем email и завершаем регистрацию, сохраняя данные пользователя."""
    user = update.message.from_user
    email = update.message.text
    context.user_data['email'] = email

    # Сохраняем данные регистрации, включая информацию, которую предоставляет Telegram
    registered_users[user.id] = {
        'name': context.user_data.get('name'),
        'email': email,
        'telegram_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    update.message.reply_text(
        "Регистрация завершена! Вот твои данные:\n"
        f"Имя: {registered_users[user.id]['name']}\n"
        f"Email: {registered_users[user.id]['email']}\n"
        f"Telegram ID: {registered_users[user.id]['telegram_id']}\n"
        f"Username: {registered_users[user.id]['username']}"
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Обработчик отмены регистрации."""
    update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

def main():
    # Замените 'YOUR_TELEGRAM_BOT_TOKEN' на токен вашего бота
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")
    dispatcher = updater.dispatcher

    # Определяем цепочку диалога для регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name_handler)],
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, email_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
