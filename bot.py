import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# ─── Configuration ──────────────────────────────────────────────────────────
# Set these in Railway environment variables:
#   BOT_TOKEN          = your bot token from @BotFather
#   OWNER_CHAT_ID      = your personal Telegram user ID (get from @userinfobot)
#   CHANNEL_URL        = https://t.me/abdulraheemaishachannel
#   WEBSITE_URL        = https://abdulraheemaisha.netlify.app/
# ─────────────────────────────────────────────────────────────────────────────

BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "YOUR_CHAT_ID_HERE")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/abdulraheemaishachannel")
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://abdulraheemaisha.netlify.app/")

# Conversation states for enquiry flow
(
    CHOOSING_SERVICE,
    ENTER_NAME,
    ENTER_DETAILS,
    CONFIRM_SEND,
) = range(4)

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Services List ───────────────────────────────────────────────────────────
SERVICES = [
    "Telegram Ads setup and management",
    "Ad rejection reviews and approval support",
    "Telegram channel promotion",
    "Custom Telegram bot development",
    "Telegram Mini App development",
]

SERVICE_EMOJI = {
    "Telegram Ads setup and management": "📢",
    "Ad rejection reviews and approval support": "✅",
    "Telegram channel promotion": "🚀",
    "Custom Telegram bot development": "🤖",
    "Telegram Mini App development": "📱",
}


# ─── Helper: Main Menu Keyboard ──────────────────────────────────────────────
def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📋 Our Services", callback_data="services")],
        [InlineKeyboardButton("💬 Send an Enquiry", callback_data="enquiry")],
        [
            InlineKeyboardButton("📢 Telegram Channel", url=CHANNEL_URL),
            InlineKeyboardButton("🌐 Website", url=WEBSITE_URL),
        ],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)


def services_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for svc in SERVICES:
        emoji = SERVICE_EMOJI.get(svc, "•")
        keyboard.append(
            [InlineKeyboardButton(f"{emoji} {svc}", callback_data=f"svc_{svc}")]
        )
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
    )


# ─── Welcome / Start ─────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    welcome = (
        f"👋 *Welcome to AbdulRaheem Aisha's Telegram Services.*\n\n"
        f"Hello {user.first_name}! I'm here to help you explore my Telegram "
        f"services and send enquiries directly to me.\n\n"
        f"*What would you like to do?*"
    )
    await update.message.reply_text(
        welcome,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


# ─── Menu Callbacks ──────────────────────────────────────────────────────────
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        welcome = (
            "🏠 *Main Menu*\n\n"
            "What would you like to do?"
        )
        await query.edit_message_text(
            welcome, parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )

    elif data == "services":
        text = (
            "📋 *Our Telegram Services*\n\n"
            "Here is what I offer:\n\n"
            "📢 *Telegram Ads setup and management*\n"
            "   Full campaign setup, targeting, and optimization.\n\n"
            "✅ *Ad rejection reviews and approval support*\n"
            "   Get your rejected ads reviewed and approved.\n\n"
            "🚀 *Telegram channel promotion*\n"
            "   Grow your channel with real, targeted members.\n\n"
            "🤖 *Custom Telegram bot development*\n"
            "   Bespoke bots for your business needs.\n\n"
            "📱 *Telegram Mini App development*\n"
            "   Interactive Mini Apps inside Telegram.\n\n"
            "Tap *Send an Enquiry* to get started!"
        )
        keyboard = [
            [InlineKeyboardButton("💬 Send an Enquiry", callback_data="enquiry")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")],
        ]
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "about":
        text = (
            "ℹ️ *About AbdulRaheem Aisha*\n\n"
            "I specialise in Telegram growth and development services — "
            "from ad management and channel promotion to custom bots and "
            "Mini Apps.\n\n"
            "🔗 *Useful Links*\n"
            f"• Channel: {CHANNEL_URL}\n"
            f"• Website: {WEBSITE_URL}\n\n"
            "Feel free to send an enquiry — I'll get back to you personally."
        )
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard()
        )

    elif data == "enquiry":
        # Start the enquiry conversation
        text = (
            "💬 *Send an Enquiry*\n\n"
            "Which service are you interested in? Tap one below."
        )
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=services_keyboard()
        )
        return CHOOSING_SERVICE


# ─── Enquiry Flow: Step 1 — Choose Service ──────────────────────────────────
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "main_menu":
        await query.edit_message_text(
            "🏠 *Main Menu*\n\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        return ConversationHandler.END

    if not data.startswith("svc_"):
        return CHOOSING_SERVICE

    service = data[4:]  # remove "svc_" prefix
    context.user_data["service"] = service

    await query.edit_message_text(
        f"✅ Selected: *{service}*\n\n"
        f"Please enter your *name* (or company name):",
        parse_mode="Markdown",
    )
    return ENTER_NAME


# ─── Enquiry Flow: Step 2 — Enter Name ──────────────────────────────────────
async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text(
            "⚠️ Please enter a valid name (at least 2 characters)."
        )
        return ENTER_NAME

    context.user_data["name"] = name
    await update.message.reply_text(
        f"Thanks, *{name}*! 👍\n\n"
        f"Now please describe your enquiry in detail.\n"
        f"Include any relevant info (budget, timeline, goals, etc.):",
        parse_mode="Markdown",
    )
    return ENTER_DETAILS


# ─── Enquiry Flow: Step 3 — Enter Details ───────────────────────────────────
async def enter_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = update.message.text.strip()
    if len(details) < 5:
        await update.message.reply_text(
            "⚠️ Please provide a bit more detail about your enquiry."
        )
        return ENTER_DETAILS

    context.user_data["details"] = details

    service = context.user_data.get("service", "N/A")
    name = context.user_data.get("name", "N/A")

    summary = (
        "📝 *Please review your enquiry:*\n\n"
        f"*Service:* {service}\n"
        f"*Name:* {name}\n"
        f"*Details:* {details}\n\n"
        "Shall I send this to AbdulRaheem Aisha?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Yes, Send", callback_data="confirm_send")],
        [InlineKeyboardButton("✏️ Edit Details", callback_data="edit_details")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")],
    ]
    await update.message.reply_text(
        summary, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRM_SEND


# ─── Enquiry Flow: Step 4 — Confirm & Send ──────────────────────────────────
async def confirm_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "edit_details":
        await query.edit_message_text(
            "✏️ Please re-enter your enquiry details:",
            parse_mode="Markdown",
        )
        return ENTER_DETAILS

    if data == "main_menu":
        await query.edit_message_text(
            "❌ Enquiry cancelled.\n\n🏠 *Main Menu*\n\nWhat would you like to do?",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard(),
        )
        # Clear user data
        context.user_data.clear()
        return ConversationHandler.END

    if data != "confirm_send":
        return CONFIRM_SEND

    # Gather data
    service = context.user_data.get("service", "N/A")
    name = context.user_data.get("name", "N/A")
    details = context.user_data.get("details", "N/A")

    user = query.from_user
    username = f"@{user.username}" if user.username else "No username"
    user_id = user.id

    # Build the message to the owner
    owner_msg = (
        "🔔 *New Enquiry from Your Bot*\n\n"
        f"*Service:* {service}\n"
        f"*Name:* {name}\n"
        f"*Details:* {details}\n\n"
        "────────────────────\n"
        f"*From:* {user.full_name}\n"
        f"*Username:* {username}\n"
        f"*User ID:* `{user_id}`\n"
        f"*Profile:* [Open](tg://user?id={user_id})"
    )

    # Send to owner
    if OWNER_CHAT_ID and OWNER_CHAT_ID != "YOUR_CHAT_ID_HERE":
        try:
            await context.bot.send_message(
                chat_id=OWNER_CHAT_ID,
                text=owner_msg,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        except Exception as e:
            logger.error(f"Failed to send enquiry to owner: {e}")
            await query.edit_message_text(
                "⚠️ There was an issue sending your enquiry. "
                "Please try again later or contact me directly.",
                reply_markup=back_to_menu_keyboard(),
            )
            context.user_data.clear()
            return ConversationHandler.END
    else:
        logger.warning("OWNER_CHAT_ID is not configured. Enquiry not forwarded.")

    # Confirm to user
    await query.edit_message_text(
        "✅ *Enquiry Sent!*\n\n"
        "Thank you! Your enquiry has been forwarded to AbdulRaheem Aisha. "
        "You'll receive a personal response soon.\n\n"
        "In the meantime, feel free to explore:\n"
        f"📢 [Telegram Channel]({CHANNEL_URL})\n"
        f"🌐 [Website]({WEBSITE_URL})",
        parse_mode="Markdown",
        reply_markup=back_to_menu_keyboard(),
        disable_web_page_preview=True,
    )

    context.user_data.clear()
    return ConversationHandler.END


# ─── Cancel Command ──────────────────────────────────────────────────────────
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Enquiry cancelled.\n\n🏠 *Main Menu*\n\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


# ─── Help Command ────────────────────────────────────────────────────────────
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🤖 *Help & Commands*\n\n"
        "/start — Show the main menu\n"
        "/services — View all services\n"
        "/enquiry — Start a new enquiry\n"
        "/about — About AbdulRaheem Aisha\n"
        "/help — Show this help message\n"
        "/cancel — Cancel an ongoing enquiry\n\n"
        "Or simply tap the buttons in the menu!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


# ─── Services Command ────────────────────────────────────────────────────────
async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📋 *Our Telegram Services*\n\n"
        "📢 Telegram Ads setup and management\n"
        "✅ Ad rejection reviews and approval support\n"
        "🚀 Telegram channel promotion\n"
        "🤖 Custom Telegram bot development\n"
        "📱 Telegram Mini App development\n\n"
        "Use /enquiry to get started!"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard()
    )


# ─── Enquiry Command ─────────────────────────────────────────────────────────
async def enquiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (
        "💬 *Send an Enquiry*\n\n"
        "Which service are you interested in? Tap one below."
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=services_keyboard()
    )
    return CHOOSING_SERVICE


# ─── About Command ───────────────────────────────────────────────────────────
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "ℹ️ *About AbdulRaheem Aisha*\n\n"
        "I specialise in Telegram growth and development services — "
        "from ad management and channel promotion to custom bots and Mini Apps.\n\n"
        "🔗 *Useful Links*\n"
        f"• Channel: {CHANNEL_URL}\n"
        f"• Website: {WEBSITE_URL}"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=back_to_menu_keyboard()
    )


# ─── Error Handler ───────────────────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Something went wrong. Please try /start again."
            )
        except Exception:
            pass


# ─── Main ────────────────────────────────────────────────────────────────────
def main() -> None:
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN is not set! Set it in environment variables.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for the enquiry flow
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_callback, pattern="^enquiry$"),
            CommandHandler("enquiry", enquiry_command),
        ],
        states={
            CHOOSING_SERVICE: [
                CallbackQueryHandler(choose_service, pattern="^(svc_|main_menu)")
            ],
            ENTER_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_name)
            ],
            ENTER_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_details)
            ],
            CONFIRM_SEND: [
                CallbackQueryHandler(confirm_send, pattern="^(confirm_send|edit_details|main_menu)$")
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
        per_user=True,
        per_chat=True,
        allow_reentry=True,
    )

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(conv_handler)

    # Menu callbacks that aren't part of the conversation
    application.add_handler(
        CallbackQueryHandler(
            menu_callback, pattern="^(main_menu|services|about)$"
        )
    )

    # Error handler
    application.add_error_handler(error_handler)

    # Start polling
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
