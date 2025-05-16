import os
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# ==== НАЛАШТУВАННЯ ====
BOT_TOKEN = "8143693954:AAE6ayEdS1xZ8BeZ-pz43Ivm1NKSOTK8QSM"
ADMIN_ID = 1345239767
 # 🔹 Замiни на свій Telegram ID

# ==== СТАНИ ====
CONSULT_NAME, CONSULT_PHONE = range(2)
BUY_NAME, BUY_PHONE, BUY_AREA, BUY_REGION, BUY_BUDGET = range(2, 7)

# ==== МЕНЮ ====
main_menu = ReplyKeyboardMarkup([
    ["📝 Залишити заявку на консультацію"],
    ["🏡 Заявка на придбання Таунхауса"],
    ["📦 Отримати візуалізацію"],
    ["📢 Перейти в канал", "ℹ️ Про компанію"]
], resize_keyboard=True)

# ==== /START ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Вітаю! Я бот компанії з нерухомості в Одесі 🏡\n\nОбери дію нижче:",
        reply_markup=main_menu
    )

# ==== ЗАЯВКА НА КОНСУЛЬТАЦІЮ ====
async def consult_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Як вас звати?")
    return CONSULT_NAME 

async def consult_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введіть ваш номер телефону:")
    return CONSULT_PHONE

async def consult_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Дякуємо! Заявку прийнято. Ми з вами зв’яжемось 📞")

    msg = (
        "📥 Нова заявка на консультацію:\n"
        f"👤 Ім’я: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return ConversationHandler.END

# ==== ЗАЯВКА НА ТАУНХАУС ====
async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Як вас звати?")
    return BUY_NAME

async def buy_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введіть ваш номер телефону:")
    return BUY_PHONE

async def buy_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Вкажіть бажану площу (наприклад: 80-120 м²):")
    return BUY_AREA

async def buy_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["area"] = update.message.text
    await update.message.reply_text("В якому районі Одеси бажаєте житло?")
    return BUY_REGION

async def buy_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["region"] = update.message.text
    await update.message.reply_text("Який бюджет на покупку? (наприклад: 60000-90000 $)")
    return BUY_BUDGET

async def buy_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["budget"] = update.message.text
    await update.message.reply_text("Дякуємо! Ми підберемо для вас найкращі варіанти 🏘️")

    msg = (
        "🏡 Нова заявка на придбання Таунхауса:\n"
        f"👤 Ім’я: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n"
        f"📐 Площа: {context.user_data['area']}\n"
        f"📍 Район: {context.user_data['region']}\n"
        f"💰 Бюджет: {context.user_data['budget']}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return ConversationHandler.END

# ==== ВІЗУАЛІЗАЦІЯ ====
async def send_visual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Шлях до папки з візуалізаціями
        folder_path = "data/visualizations"
        
        # Отримуємо список всіх файлів у папці
        image_files = [f for f in os.listdir(folder_path) if f.startswith("visual") and f.endswith(".jpeg")]
        
        if image_files:
            # Відправляємо всі зображення
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                with open(image_path, "rb") as photo:
                    await update.message.reply_photo(photo)
        else:
            await update.message.reply_text("Візуалізації поки що немає.")
    except FileNotFoundError:
        await update.message.reply_text("Файл візуалізації ще не додано.")

# ==== КАНАЛ ====
async def go_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Переходь у наш канал 👉 https://t.me/RCG_nedvigimost")

# ==== ПРО КОМПАНІЮ ====
async def about_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏘Ми будівельна компанія Realty Consulting Group що має багаторічний досвід в будівництві, з початку повномасштабного вторгнення ворога, ми побудували більше ніж 300 будинків в місті Одеса. Дякуємо що довіряєте та обираєте саме нас.🤝"
        "📞 Консультації та підтримка: +380 93 912 14 14\n"
        "🌐 Сайт: https://rcg-od.mssg.me/\n"
        "📸 Instagram: https://www.instagram.com/realty_consulting?igsh=dGVtY3d1NTh2ZWRn&utm_source=qr"
    )

# ==== НЕВІДОМА КОМАНДА ====
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Не розпізнав команду. Оберіть дію з меню 👇")

# ==== ЗАПУСК ====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # --- Заявка на консультацію
    consult_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(".*консультацію.*"), consult_start)],
        states={
            CONSULT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, consult_name)],
            CONSULT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consult_phone)],
        },
        fallbacks=[]
    )

    # --- Заявка на Таунхаус
    buy_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(".*Таунхауса.*"), buy_start)],
        states={
            BUY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_name)],
            BUY_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_phone)],
            BUY_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_area)],
            BUY_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_region)],
            BUY_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_budget)],
        },
        fallbacks=[]
    )

    # --- Меню
    app.add_handler(CommandHandler("start", start))
    app.add_handler(consult_conv)
    app.add_handler(buy_conv)
    app.add_handler(MessageHandler(filters.Regex(".*візуалізацію.*"), send_visual))
    app.add_handler(MessageHandler(filters.Regex(".*канал.*"), go_to_channel))
    app.add_handler(MessageHandler(filters.Regex(".*компанію.*"), about_company))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    print("✅ Бот запущений!")
    app.run_polling()

if __name__ == "__main__":
    main()
