import os
import logging
from telegram import Update, ReplyKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ==== CONFIGURATION ====
# Get the token from environment variable with fallback to hardcoded value
BOT_TOKEN = os.getenv("BOT_TOKEN", "7331886812:AAGBtC0OqSQhZy2Z0gQnNTeHRJZRf6i5Y9I")
# Get the admin ID from environment variable with fallback to hardcoded value
ADMIN_ID = int(os.getenv("ADMIN_ID", "1345239767"))

# ==== CONVERSATION STATES ====
CONSULT_NAME, CONSULT_PHONE = range(2)
BUY_NAME, BUY_PHONE, BUY_AREA, BUY_REGION, BUY_BUDGET = range(2, 7)
CALC_AREA, CALC_ROOMS, CALC_LOCATION = range(7, 10)

# ==== KEYBOARD MENUS ====
main_menu = ReplyKeyboardMarkup([
    ["📝 Залишити заявку на консультацію"],
    ["🏡 Заявка на придбання Таунхауса"],
    ["📦 Отримати візуалізацію"],
    ["💰 Калькулятор ціни", "❓ Часті питання"],
    ["📢 Перейти в канал", "ℹ️ Про компанію"]
], resize_keyboard=True)

# FAQ options menu
faq_menu = ReplyKeyboardMarkup([
    ["Процес покупки", "Умови оплати"],
    ["Документи", "Терміни будівництва"],
    ["Інфраструктура", "Повернутись до меню"]
], resize_keyboard=True)

# ==== COMMAND HANDLERS ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for the /start command - sends welcome message with main menu"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    await update.message.reply_text(
        f"Вітаю, {user.first_name}! Я бот компанії з нерухомості в Одесі 🏡\n\nОбери дію нижче:",
        reply_markup=main_menu
    )

# ==== CONSULTATION REQUEST HANDLERS ====
async def consult_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates consultation request conversation"""
    logger.info(f"User {update.effective_user.id} started consultation request")
    
    await update.message.reply_text("Як вас звати?")
    return CONSULT_NAME 

async def consult_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles consultation name input"""
    context.user_data["name"] = update.message.text
    logger.info(f"Got name for consultation: {context.user_data['name']}")
    
    await update.message.reply_text("Введіть ваш номер телефону:")
    return CONSULT_PHONE

async def consult_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles consultation phone input and completes consultation request"""
    context.user_data["phone"] = update.message.text
    logger.info(f"Got phone for consultation: {context.user_data['phone']}")
    
    await update.message.reply_text(
        "Дякуємо! Заявку прийнято. Ми з вами зв'яжемось 📞", 
        reply_markup=main_menu
    )

    # Prepare and send message to admin
    msg = (
        "📥 Нова заявка на консультацію:\n"
        f"👤 Ім'я: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        logger.info(f"Sent consultation request to admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"Failed to send message to admin: {e}")
    
    return ConversationHandler.END

# ==== TOWNHOUSE PURCHASE REQUEST HANDLERS ====
async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates townhouse purchase request conversation"""
    logger.info(f"User {update.effective_user.id} started townhouse purchase request")
    
    await update.message.reply_text("Як вас звати?")
    return BUY_NAME

async def buy_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles purchase name input"""
    context.user_data["name"] = update.message.text
    logger.info(f"Got name for purchase: {context.user_data['name']}")
    
    await update.message.reply_text("Введіть ваш номер телефону:")
    return BUY_PHONE

async def buy_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles purchase phone input"""
    context.user_data["phone"] = update.message.text
    logger.info(f"Got phone for purchase: {context.user_data['phone']}")
    
    await update.message.reply_text("Вкажіть бажану площу (наприклад: 80-120 м²):")
    return BUY_AREA

async def buy_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles purchase area input"""
    context.user_data["area"] = update.message.text
    logger.info(f"Got area for purchase: {context.user_data['area']}")
    
    await update.message.reply_text("В якому районі Одеси бажаєте житло?")
    return BUY_REGION

async def buy_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles purchase region input"""
    context.user_data["region"] = update.message.text
    logger.info(f"Got region for purchase: {context.user_data['region']}")
    
    await update.message.reply_text("Який бюджет на покупку? (наприклад: 60000-90000 $)")
    return BUY_BUDGET

async def buy_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles purchase budget input and completes purchase request"""
    context.user_data["budget"] = update.message.text
    logger.info(f"Got budget for purchase: {context.user_data['budget']}")
    
    await update.message.reply_text(
        "Дякуємо! Ми підберемо для вас найкращі варіанти 🏘️", 
        reply_markup=main_menu
    )

    # Prepare and send message to admin
    msg = (
        "🏡 Нова заявка на придбання Таунхауса:\n"
        f"👤 Ім'я: {context.user_data['name']}\n"
        f"📱 Телефон: {context.user_data['phone']}\n"
        f"📐 Площа: {context.user_data['area']}\n"
        f"📍 Район: {context.user_data['region']}\n"
        f"💰 Бюджет: {context.user_data['budget']}"
    )
    
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
        logger.info(f"Sent purchase request to admin {ADMIN_ID}")
    except Exception as e:
        logger.error(f"Failed to send message to admin: {e}")
    
    return ConversationHandler.END

# ==== VISUALIZATION HANDLERS ====
async def send_visual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends visualization images to the user"""
    logger.info(f"User {update.effective_user.id} requested visualizations")
    
    try:
        # Path to the visualization folder
        folder_path = "data/visualizations"
        
        # Шукаємо лише JPEG файли, які ви надали
        image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpeg")]
        
        # Якщо JPEG-файлів немає, перевіряємо SVG (будуть надіслані як документи)
        if not image_files:
            image_files = [f for f in os.listdir(folder_path) if f.endswith(".svg")]
        
        if image_files:
            # Send message first
            await update.message.reply_text("Ось візуалізації наших таунхаусів:")
            
            # Send all images
            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                try:
                    # For SVG files, we need to send them as documents because Telegram can't process SVGs as photos
                    if image_file.endswith(".svg"):
                        with open(image_path, "rb") as document:
                            await update.message.reply_document(document, filename=image_file)
                            logger.info(f"Sent visualization as document: {image_file}")
                    else:
                        with open(image_path, "rb") as photo:
                            await update.message.reply_photo(photo)
                            logger.info(f"Sent visualization as photo: {image_file}")
                except Exception as e:
                    logger.error(f"Failed to send image {image_file}: {e}")
                    continue
                    
            # Send final message after all images
            await update.message.reply_text(
                "Якщо зацікавились, залиште заявку на консультацію або покупку!",
                reply_markup=main_menu
            )
        else:
            await update.message.reply_text(
                "На жаль, зараз візуалізації недоступні. Спробуйте пізніше або зверніться до нашого менеджера.",
                reply_markup=main_menu
            )
    except FileNotFoundError:
        logger.error(f"Visualization folder not found: {folder_path}")
        await update.message.reply_text(
            "На жаль, зараз візуалізації недоступні. Спробуйте пізніше або зверніться до нашого менеджера.",
            reply_markup=main_menu
        )
    except Exception as e:
        logger.error(f"Error sending visualizations: {e}")
        await update.message.reply_text(
            "Виникла помилка при отриманні візуалізацій. Спробуйте пізніше.",
            reply_markup=main_menu
        )

# ==== PRICE CALCULATOR HANDLERS ====
async def calc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates price calculator conversation"""
    logger.info(f"User {update.effective_user.id} started price calculator")
    
    # Clear any existing data
    context.user_data.clear()
    
    # Create keyboard with area options
    area_keyboard = ReplyKeyboardMarkup([
        ["60-80 м²", "80-100 м²"],
        ["100-120 м²", "120-150 м²"],
        ["Повернутись до меню"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "🧮 Калькулятор ціни на таунхаус\n\n"
        "Виберіть бажану площу:",
        reply_markup=area_keyboard
    )
    return CALC_AREA

async def calc_area(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles area selection for price calculator"""
    # If user wants to return to main menu
    if update.message.text == "Повернутись до меню":
        await update.message.reply_text("Повертаємось до головного меню", reply_markup=main_menu)
        return ConversationHandler.END
    
    # Save selected area
    if "Повернутись до меню" not in update.message.text:
        context.user_data["area"] = update.message.text
        logger.info(f"User selected area: {context.user_data['area']}")
    
    # Create keyboard with room options
    room_keyboard = ReplyKeyboardMarkup([
        ["2 кімнати", "3 кімнати"],
        ["4 кімнати", "5+ кімнат"],
        ["Повернутись до меню"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "Виберіть кількість кімнат:",
        reply_markup=room_keyboard
    )
    return CALC_ROOMS

async def calc_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles room selection for price calculator"""
    # If user wants to return to main menu
    if update.message.text == "Повернутись до меню":
        await update.message.reply_text("Повертаємось до головного меню", reply_markup=main_menu)
        return ConversationHandler.END
    
    # Save selected rooms
    context.user_data["rooms"] = update.message.text
    logger.info(f"User selected rooms: {context.user_data['rooms']}")
    
    # Create keyboard with location options
    location_keyboard = ReplyKeyboardMarkup([
        ["Київський район", "Приморський район"],
        ["Малиновський район", "Суворовський район"],
        ["Повернутись до меню"]
    ], resize_keyboard=True)
    
    await update.message.reply_text(
        "Виберіть район Одеси:",
        reply_markup=location_keyboard
    )
    return CALC_LOCATION

async def calc_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calculates and displays the estimated price"""
    # If user wants to return to main menu
    if update.message.text == "Повернутись до меню":
        await update.message.reply_text("Повертаємось до головного меню", reply_markup=main_menu)
        return ConversationHandler.END
    
    # Save selected location
    context.user_data["location"] = update.message.text
    logger.info(f"User selected location: {context.user_data['location']}")
    
    # Calculate base price based on area
    area = context.user_data["area"]
    if area == "60-80 м²":
        base_price = 60000
    elif area == "80-100 м²":
        base_price = 80000
    elif area == "100-120 м²":
        base_price = 100000
    else:  # 120-150 м²
        base_price = 120000
    
    # Apply room multiplier
    rooms = context.user_data["rooms"]
    if rooms == "2 кімнати":
        room_multiplier = 1.0
    elif rooms == "3 кімнати":
        room_multiplier = 1.1
    elif rooms == "4 кімнати":
        room_multiplier = 1.2
    else:  # 5+ rooms
        room_multiplier = 1.3
    
    # Apply location multiplier
    location = context.user_data["location"]
    if location == "Київський район":
        location_multiplier = 1.2
    elif location == "Приморський район":
        location_multiplier = 1.3
    elif location == "Малиновський район":
        location_multiplier = 1.1
    else:  # Суворовський район
        location_multiplier = 1.0
    
    # Calculate final price
    final_price = int(base_price * room_multiplier * location_multiplier)
    
    # Format prices for display
    base_price_formatted = "{:,}".format(base_price).replace(",", " ")
    final_price_formatted = "{:,}".format(final_price).replace(",", " ")
    
    # Prepare and send result message
    result_message = (
        f"📊 Результати розрахунку ціни таунхаусу:\n\n"
        f"🏠 Площа: {area}\n"
        f"🚪 Кімнат: {rooms}\n"
        f"📍 Район: {location}\n\n"
        f"💵 Базова ціна: ${base_price_formatted}\n"
        f"💰 Орієнтовна вартість: ${final_price_formatted}\n\n"
        f"⚠️ Це приблизна оцінка. Для точної вартості залиште заявку на консультацію."
    )
    
    await update.message.reply_text(result_message, reply_markup=main_menu)
    return ConversationHandler.END

# ==== FAQ HANDLERS ====
async def faq_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows FAQ categories menu"""
    logger.info(f"User {update.effective_user.id} requested FAQ")
    
    await update.message.reply_text(
        "❓ Часті питання\n\n"
        "Оберіть категорію питання:", 
        reply_markup=faq_menu
    )

async def faq_buying_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows information about buying process"""
    logger.info(f"User {update.effective_user.id} requested FAQ about buying process")
    
    await update.message.reply_text(
        "🔄 Процес покупки таунхаусу:\n\n"
        "1️⃣ Консультація з менеджером та вибір об'єкту\n"
        "2️⃣ Резервування об'єкту (внесення передоплати)\n"
        "3️⃣ Підготовка та підписання договору\n"
        "4️⃣ Оплата згідно з обраним графіком\n"
        "5️⃣ Отримання ключів та документів\n\n"
        "Для старту процесу оберіть 'Залишити заявку на консультацію' в головному меню.",
        reply_markup=faq_menu
    )

async def faq_payment_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows information about payment terms"""
    logger.info(f"User {update.effective_user.id} requested FAQ about payment terms")
    
    await update.message.reply_text(
        "💳 Умови оплати:\n\n"
        "✅ Повна оплата: знижка 5%\n"
        "✅ Розстрочка на 12 місяців: перший внесок 30%\n"
        "✅ Розстрочка на 24 місяці: перший внесок 40%\n"
        "✅ Розстрочка на 36 місяців: перший внесок 50%\n\n"
        "💰 Ми також співпрацюємо з банками для оформлення іпотеки.\n"
        "📞 Для отримання детальної інформації залиште заявку на консультацію.",
        reply_markup=faq_menu
    )

async def faq_documents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows information about required documents"""
    logger.info(f"User {update.effective_user.id} requested FAQ about documents")
    
    await update.message.reply_text(
        "📄 Необхідні документи:\n\n"
        "👤 Для резервування:\n"
        "- Паспорт та ІПН\n\n"
        "📝 Для підписання договору:\n"
        "- Паспорт та ІПН\n"
        "- Документи, що підтверджують сімейний стан\n\n"
        "🏠 При передачі нерухомості:\n"
        "- Ви отримаєте повний пакет документів на право власності\n"
        "- Технічний паспорт\n"
        "- Акт прийому-передачі",
        reply_markup=faq_menu
    )

async def faq_construction_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows information about construction time"""
    logger.info(f"User {update.effective_user.id} requested FAQ about construction time")
    
    await update.message.reply_text(
        "⏱️ Терміни будівництва:\n\n"
        "🏗️ Стандартний термін будівництва таунхаусу - 12-18 місяців\n\n"
        "📅 Етапи будівництва:\n"
        "1. Підготовка ділянки та фундамент: 2-3 місяці\n"
        "2. Зведення коробки будинку: 4-6 місяців\n"
        "3. Внутрішні та зовнішні комунікації: 2-3 місяці\n"
        "4. Оздоблювальні роботи: 4-6 місяців\n\n"
        "🔍 Ви можете відслідковувати прогрес будівництва через фото-звіти, які ми регулярно публікуємо в нашому каналі.",
        reply_markup=faq_menu
    )

async def faq_infrastructure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows information about infrastructure"""
    logger.info(f"User {update.effective_user.id} requested FAQ about infrastructure")
    
    await update.message.reply_text(
        "🏙️ Інфраструктура наших комплексів:\n\n"
        "✅ Закрита територія з охороною та відеонаглядом\n"
        "✅ Паркінг для мешканців та гостей\n"
        "✅ Дитячі та спортивні майданчики\n"
        "✅ Зони відпочинку та барбекю\n"
        "✅ Ландшафтний дизайн території\n\n"
        "🏪 Поруч з нашими комплексами зазвичай розташовані:\n"
        "- Супермаркети та магазини\n"
        "- Школи та дитячі садки\n"
        "- Медичні заклади\n"
        "- Зупинки громадського транспорту",
        reply_markup=faq_menu
    )

async def return_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Returns to main menu"""
    logger.info(f"User {update.effective_user.id} returned to main menu")
    
    await update.message.reply_text(
        "Повертаємось до головного меню",
        reply_markup=main_menu
    )

# ==== CHANNEL AND COMPANY INFO HANDLERS ====
async def go_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides link to company channel"""
    logger.info(f"User {update.effective_user.id} requested channel link")
    
    await update.message.reply_text(
        "Переходь у наш канал 👉 https://t.me/RCG_nedvigimost",
        reply_markup=main_menu
    )

async def about_company(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Provides information about the company"""
    logger.info(f"User {update.effective_user.id} requested company info")
    
    await update.message.reply_text(
        "🏘 Ми будівельна компанія Realty Consulting Group що має багаторічний досвід в будівництві. "
        "З початку повномасштабного вторгнення ворога, ми побудували більше ніж 300 будинків в місті Одеса. "
        "Дякуємо що довіряєте та обираєте саме нас.🤝\n\n"
        "📞 Консультації та підтримка: +380 93 912 14 14\n"
        "🌐 Сайт: https://rcg-od.mssg.me/\n"
        "📸 Instagram: https://www.instagram.com/realty_consulting?igsh=dGVtY3d1NTh2ZWRn&utm_source=qr",
        reply_markup=main_menu
    )

# ==== FALLBACK HANDLER ====
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for unknown messages"""
    logger.info(f"User {update.effective_user.id} sent unknown message: {update.message.text}")
    
    await update.message.reply_text(
        "Не розпізнав команду. Оберіть дію з меню 👇",
        reply_markup=main_menu
    )

# ==== MAIN FUNCTION ====
def main():
    """Main function to start the bot"""
    try:
        # Create the application
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        
        # Create conversation handlers
        consult_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(".*консультацію.*"), consult_start)],
            states={
                CONSULT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, consult_name)],
                CONSULT_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, consult_phone)],
            },
            fallbacks=[CommandHandler("start", start)]
        )
        
        buy_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(".*Таунхауса.*"), buy_start)],
            states={
                BUY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_name)],
                BUY_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_phone)],
                BUY_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_area)],
                BUY_REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_region)],
                BUY_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_budget)],
            },
            fallbacks=[CommandHandler("start", start)]
        )
        
        # Create calculator conversation handler
        calc_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(".*Калькулятор ціни.*"), calc_start)],
            states={
                CALC_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_area)],
                CALC_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_rooms)],
                CALC_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, calc_location)],
            },
            fallbacks=[CommandHandler("start", start)]
        )
        
        # Add handlers to the application
        app.add_handler(CommandHandler("start", start))
        app.add_handler(consult_conv)
        app.add_handler(buy_conv)
        app.add_handler(calc_conv)
        app.add_handler(MessageHandler(filters.Regex(".*візуалізацію.*"), send_visual))
        app.add_handler(MessageHandler(filters.Regex(".*Часті питання.*"), faq_start))
        app.add_handler(MessageHandler(filters.Regex("Процес покупки"), faq_buying_process))
        app.add_handler(MessageHandler(filters.Regex("Умови оплати"), faq_payment_terms))
        app.add_handler(MessageHandler(filters.Regex("Документи"), faq_documents))
        app.add_handler(MessageHandler(filters.Regex("Терміни будівництва"), faq_construction_time))
        app.add_handler(MessageHandler(filters.Regex("Інфраструктура"), faq_infrastructure))
        app.add_handler(MessageHandler(filters.Regex("Повернутись до меню"), return_to_menu))
        app.add_handler(MessageHandler(filters.Regex(".*канал.*"), go_to_channel))
        app.add_handler(MessageHandler(filters.Regex(".*компанію.*"), about_company))
        app.add_handler(MessageHandler(filters.TEXT, unknown))
        
        # Start the bot
        logger.info("✅ Bot is starting...")
        print("✅ Бот запущений!")
        
        # Create visualization directory if it doesn't exist
        os.makedirs("data/visualizations", exist_ok=True)
        
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Error starting the bot: {e}")
        print(f"❌ Error starting the bot: {e}")

if __name__ == "__main__":
    main()
