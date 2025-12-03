import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "7784272414:AAEcJPgF0yYVqljYeBgorHO8gYEIXNKVQAA"

# Список стартовых картинок
start_images = [
    "img/start1.jpeg",
    "img/start2.jpeg",
    "img/start3.jpeg",
    "img/start4.jpeg"
]

# Кнопки меню
def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 Платформа", callback_data="locked")],
        [InlineKeyboardButton("🔴 Анализ", callback_data="locked")],
        [InlineKeyboardButton("🟢 Промо", callback_data="promo")],
        [InlineKeyboardButton("🔴 Другое", callback_data="locked")]
    ])

caption = (
    "Здраствуйте, меня зовут Максат Рустемов!\n\n"
    "Этот бот создан как помощник к моему основному каналу, "
    "где я публикую новости, свою работу, графики и аналитику валют.\n\n"
    "Здесь вы получите удобный доступ к функциям, подсказкам и материалам, "
    "а все актуальные новости публикуются в основном канале:\n"
    "https://t.me/+0KT1m82EBqMwZmE6\n\n"
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img_path = random.choice(start_images)
    keyboard = get_menu()
    
    with open(img_path, "rb") as img:
        await update.message.reply_photo(photo=img, caption=caption, reply_markup=keyboard)

# Обработчик кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "locked":
        await query.answer(text="Этот раздел пока недоступен 🔒", show_alert=True)
        return

    elif query.data == "promo":
        # Удаляем главное сообщение через 4 секунды
        await asyncio.sleep(1)  # чтобы edit прошло до удаления
        await query.message.delete()
        
        # Просим ввести ID трейдера
        msg = await query.message.chat.send_message("Введите ваш ID трейдера:")
        context.user_data["state"] = "waiting_for_id"
        context.user_data["temp_msg"] = msg

# Обработчик сообщений
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    
    if state == "waiting_for_id":
        # Сохраняем ID трейдера
        context.user_data["trader_id"] = update.message.text
        await update.message.delete()  # удаляем сообщение пользователя
        await context.user_data["temp_msg"].delete()  # удаляем сообщение бота
        msg = await update.message.chat.send_message("Введите промокод:")
        context.user_data["state"] = "waiting_for_promo"
        context.user_data["temp_msg"] = msg

    elif state == "waiting_for_promo":
        context.user_data["promo_code"] = update.message.text
        await update.message.delete()
        await context.user_data["temp_msg"].delete()
        
        # Промокод загружен
        msg = await update.message.chat.send_message("🚫 Промокод уже использован!")
        await asyncio.sleep(4)
        await msg.delete()
        
        # Сбрасываем состояние
        context.user_data["state"] = None
        
        # Показываем главное меню снова
        img_path = random.choice(start_images)
        keyboard = get_menu()
        with open(img_path, "rb") as img:
            await update.message.chat.send_photo(photo=img, caption=caption, reply_markup=keyboard)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("Бот запущен...")
    app.run_polling()
