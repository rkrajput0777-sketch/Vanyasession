#!/usr/bin/env python3
import logging
import os
import time
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot statistics
bot_stats = {
    'start_time': time.time(),
    'total_users': set(),
    'sessions_generated': 0,
    'total_commands': 0
}

# Try different import methods
try:
    # Method 1: Direct imports
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    from telegram.constants import ParseMode
    logger.info("SUCCESS: Using direct imports")
except ImportError:
    try:
        # Method 2: Private imports
        from telegram._update import Update
        from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
        from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
        from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
        from telegram.constants import ParseMode
        logger.info("SUCCESS: Using private imports")
    except ImportError as e:
        logger.error(f"Failed to import telegram modules: {e}")
        exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        user = update.effective_user
        bot = context.bot
        
        # Track user
        bot_stats['total_users'].add(user.id)
        bot_stats['total_commands'] += 1
        
        # Get clickable mentions
        mention_user = user.mention_html()
        mention_bot = f'<a href="tg://user?id={bot.id}">{bot.first_name}</a>'
        clickable_name = '<a href="https://t.me/noturrsem">ηᴏᴛᴜʀʀsᴇᴍ</a>'
        
        message = f"""<b>┌────── ˹ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ˼─── ⏤͟͞●
┆◍ ʜᴇʏ {mention_user}
┆◍ ɪ'ᴍ : {mention_bot}
└──────────────────────•
 ❀ ɪ'ᴍ ᴀ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴇʀ ʙᴏᴛ.
 ✤ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ.
 ❃ 𝛅ᴜᴘᴘᴏʀᴛ - ᴘʏʀᴏɢʀᴀᴍ | ᴛᴇʟᴇᴛʜᴏɴ.
 ✮ ηᴏ ɪᴅ ʟᴏɢ ᴏᴜᴛ ɪssᴜᴇ & ғᴜʟʟ sᴇᴄᴜʀᴇ.
•────────────────────────•
 ❖ 𝐏ᴏᴡᴇʀᴇᴅ ʙʏ  :-  {clickable_name}
•────────────────────────•</b>"""
        
        # Create inline keyboard with buttons
        keyboard = [
            [InlineKeyboardButton("• ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ •", callback_data='generate_session')],
            [InlineKeyboardButton("• ʙᴀsɪᴄ ɢᴜɪᴅᴇs •", callback_data='basic_guides')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Convert Google Drive link to direct download link
        image_url = "https://drive.google.com/uc?export=download&id=1lDE4KpTwM9aq9OlNYHEE-lnreUUDgGg-"
        
        await update.message.reply_photo(
            photo=image_url,
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in start function: {e}")
        # Fallback to text message
        await update.message.reply_text(
            "<b>🤖 Bot is running! Use /gen to generate session strings.</b>",
            parse_mode=ParseMode.HTML
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'generate_session':
        keyboard = [
            [InlineKeyboardButton("❤️ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ 💛", callback_data='gen_main')],
            [InlineKeyboardButton("✦ ʙᴀᴄᴋ ✦", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """<b>🔥 sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ 🔥

ᴄʜᴏᴏsᴇ ʏᴏᴜʀ ᴘʀᴇғᴇʀʀᴇᴅ ʟɪʙʀᴀʀʏ:

💎 ᴘʏʀᴏɢʀᴀᴍ - ғᴀsᴛ & ᴍᴏᴅᴇʀɴ
💎 ᴛᴇʟᴇᴛʜᴏɴ - sᴛᴀʙʟᴇ & ʀᴇʟɪᴀʙʟᴇ

✨ ғᴇᴀᴛᴜʀᴇs:
• 2ғᴀ sᴜᴘᴘᴏʀᴛ
• ɴᴏ ʟᴏɢᴏᴜᴛ ɪssᴜᴇs
• sᴇᴄᴜʀᴇ ᴘʀᴏᴄᴇss
• ʀᴇᴀʟ ᴏᴛᴘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ</b>"""
        
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    elif query.data == 'basic_guides':
        keyboard = [
            [InlineKeyboardButton("✦ ʙᴀᴄᴋ ✦", callback_data='back_to_start')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """<b>✦ ʙᴀsɪᴄ ᴄᴏᴍᴍᴀɴᴅs

➻ ᴛʏᴘᴇ /gen ᴏʀ ᴛᴀᴘ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ ғᴏʀ ɢᴇɴ sᴇssɪᴏɴ.

➻ ᴛʏᴘᴇ /ping ᴄʜᴇᴀᴋ ʙᴏᴛ ᴜᴘᴛɪᴍᴇ

➻ ᴛʏᴘᴇ /stats ғᴏʀ ᴄʜᴇᴀᴋ ʙᴏᴛ sᴛᴀᴛs

➻ ᴛʏᴘᴇ /broadcast sᴇɴᴅ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴜsᴇʀs + ᴄʜᴀᴛ (ᴏɴʟʏ ᴏᴡɴᴇʀ ᴜsᴇʀ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ)</b>"""
        
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /gen command."""
    bot_stats['total_commands'] += 1
    
    keyboard = [
        [InlineKeyboardButton("❤️ ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ 💛", callback_data='gen_main')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """<b>🔥 sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ 🔥

ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ sᴛᴀʀᴛ ɢᴇɴᴇʀᴀᴛɪɴɢ ʏᴏᴜʀ sᴇssɪᴏɴ sᴛʀɪɴɢ!</b>"""
    
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ping command."""
    bot_stats['total_commands'] += 1
    
    start_time = time.time()
    current_time = time.time()
    uptime = current_time - bot_stats['start_time']
    
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    ping_time = (time.time() - start_time) * 1000
    
    message = f"""<b>🏓 ᴘᴏɴɢ!

⚡ ᴘɪɴɢ: {ping_time:.0f}ᴍs
⏰ ᴜᴘᴛɪᴍᴇ: {hours}ʜ {minutes}ᴍ {seconds}s
🤖 sᴛᴀᴛᴜs: ᴀᴄᴛɪᴠᴇ ✅</b>"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command."""
    bot_stats['total_commands'] += 1
    
    current_time = time.time()
    uptime = current_time - bot_stats['start_time']
    
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    
    message = f"""<b>📊 ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs

👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: {len(bot_stats['total_users'])}
🔥 sᴇssɪᴏɴs ɢᴇɴᴇʀᴀᴛᴇᴅ: {bot_stats['sessions_generated']}
💫 ᴛᴏᴛᴀʟ ᴄᴏᴍᴍᴀɴᴅs: {bot_stats['total_commands']}
⏰ ᴜᴘᴛɪᴍᴇ: {hours}ʜ {minutes}ᴍ {seconds}s
📅 sᴛᴀʀᴛᴇᴅ: {datetime.fromtimestamp(bot_stats['start_time']).strftime('%Y-%m-%d %H:%M:%S')}</b>"""
    
    await update.message.reply_text(message, parse_mode=ParseMode.HTML)

def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN environment variable is not set!")
        logger.info("Please set your Telegram bot token using the secrets management.")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gen", gen_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bot is starting...")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()