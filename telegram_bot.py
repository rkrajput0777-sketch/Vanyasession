#!/usr/bin/env python3
import logging
import os
import time
import asyncio
import tempfile
import re
from datetime import datetime
from typing import Dict, Any, Optional, Union
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, User
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import ParseMode
from pyrogram.client import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneNumberInvalid
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneNumberInvalidError

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# States for conversation handler
PHONE_NUMBER, OTP_CODE, TWO_FA_PASSWORD = range(3)

# Bot statistics
bot_stats: Dict[str, Any] = {
    'start_time': time.time(),
    'total_users': set(),
    'sessions_generated': 0,
    'total_commands': 0
}

# Session generation data storage
session_data: Dict[int, Dict[str, Any]] = {}

# Owner and log group IDs
OWNER_ID: int = 8455833782
LOG_GROUP_ID: int = -1002563257842

# Phone number validation pattern
PHONE_PATTERN = re.compile(r'\+[1-9]\d{1,3}[1-9]\d{4,14}$')

# Safe message editing function
async def edit_message_safely(query, message: str, reply_markup=None) -> None:
    """Safely edit message whether it's a photo or text message."""
    try:
        # Try editing as caption first (for photo messages)
        if reply_markup:
            await query.edit_message_caption(
                caption=message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_caption(
                caption=message,
                parse_mode=ParseMode.HTML
            )
    except:
        try:
            # Fallback to editing as text message
            if reply_markup:
                await query.edit_message_text(
                    message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text(
                    message,
                    parse_mode=ParseMode.HTML
                )
        except:
            # If both fail, send a new message
            try:
                await query.message.reply_text(
                    message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Failed to edit or send message: {e}")

# Enhanced logging function for log group
async def log_to_group(context: ContextTypes.DEFAULT_TYPE, message: str, level: str = "INFO") -> None:
    """Send logs to the designated log group."""
    try:
        log_message = f"<b>🤖 BOT LOG [{level}]</b>\n\n<code>{message}</code>\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        await context.bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=log_message,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Silently log to console only if group is not accessible
        logger.info(f"Log group not accessible, logging to console: {message}")

# Enhanced phone number validation
def validate_phone_number(phone: str) -> tuple[bool, str]:
    """Validate phone number format and provide detailed feedback."""
    if not phone:
        return False, "📱 Please enter your phone number"
    
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    if not phone.startswith("+"):
        return False, "📱 Phone number must start with + and country code\n\n🔸 Example: +1234567890"
    
    if len(phone) < 8:
        return False, "📱 Phone number is too short\n\n🔸 Include country code: +1234567890"
    
    if len(phone) > 16:
        return False, "📱 Phone number is too long\n\n🔸 Maximum 15 digits after +"
    
    if not PHONE_PATTERN.match(phone):
        return False, "📱 Invalid phone number format\n\n🔸 Use format: +[country code][number]\n🔸 Example: +1234567890"
    
    return True, "✅ Valid phone number format"

# Enhanced OTP validation - only accept "1 2 3 4 5" format
def validate_otp_code(otp: str) -> tuple[bool, str]:
    """Validate OTP code format - only accepts space-separated format."""
    if not otp:
        return False, "🔢 Please enter the OTP code"
    
    otp_clean = otp.strip()
    
    # Check if it's exactly in "1 2 3 4 5" format
    parts = otp_clean.split(" ")
    
    if len(parts) != 5:
        return False, "🔢 Please use exactly this format: 1 2 3 4 5\n\n🔸 Example: 1 2 3 4 5\n🔸 Your code with spaces between each digit"
    
    # Check each part is a single digit
    for part in parts:
        if not part.isdigit() or len(part) != 1:
            return False, "🔢 Each digit must be separated by space\n\n🔸 Correct format: 1 2 3 4 5\n🔸 Wrong format: 12345 or 12 34 5"
    
    return True, "✅ Valid OTP format"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not update.effective_user or not update.message:
        return
        
    user: User = update.effective_user
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
    
    try:
        await update.message.reply_photo(
            photo=image_url,
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except:
        # Fallback to text message if image fails
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses with enhanced error handling."""
    if not update.callback_query:
        return
        
    query = update.callback_query
    try:
        await query.answer()
        
        # Log button interaction
        user_info = f"User: {query.from_user.id if query.from_user else 'Unknown'} | Action: {query.data}"
        await log_to_group(context, f"Button pressed: {user_info}", "INFO")
    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        await log_to_group(context, f"Button handler error: {e}", "ERROR")
        return
    
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
        
        try:
            await query.edit_message_caption(
                caption=message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except:
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    
    elif query.data == 'gen_main':
        keyboard = [
            [InlineKeyboardButton("🔥 ᴘʏʀᴏɢʀᴀᴍ", callback_data='pyrogram_gen'),
             InlineKeyboardButton("🔥 ᴛᴇʟᴇᴛʜᴏɴ", callback_data='telethon_gen')],
            [InlineKeyboardButton("✦ ʙᴀᴄᴋ ✦", callback_data='generate_session')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """<b>💫 sᴇʟᴇᴄᴛ ʟɪʙʀᴀʀʏ 💫

🔥 ᴘʏʀᴏɢʀᴀᴍ
• ғᴀsᴛ ᴀɴᴅ ᴍᴏᴅᴇʀɴ
• ᴇᴀsʏ ᴛᴏ ᴜsᴇ
• ʙᴇsᴛ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ

🔥 ᴛᴇʟᴇᴛʜᴏɴ  
• sᴛᴀʙʟᴇ ᴀɴᴅ ʀᴇʟɪᴀʙʟᴇ
• ᴀᴅᴠᴀɴᴄᴇᴅ ғᴇᴀᴛᴜʀᴇs
• ᴡɪᴅᴇʟʏ ᴜsᴇᴅ

⚡ ʀᴇᴀᴅʏ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ - ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ!</b>"""
        
        try:
            await query.edit_message_caption(
                caption=message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except:
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    
    elif query.data == 'pyrogram_gen':
        try:
            await start_pyrogram_session(update, context)
        except Exception as e:
            logger.error(f"Error in pyrogram session start: {e}")
            await log_to_group(context, f"Pyrogram session start error: {e}", "ERROR")
    
    elif query.data == 'telethon_gen':
        try:
            await start_telethon_session(update, context)
        except Exception as e:
            logger.error(f"Error in telethon session start: {e}")
            await log_to_group(context, f"Telethon session start error: {e}", "ERROR")
    
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
        
        try:
            await query.edit_message_caption(
                caption=message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
        except:
            await query.edit_message_text(
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
    
    elif query.data == 'back_to_start':
        await start_from_callback(update, context)

async def start_from_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Recreate start message from callback."""
    query = update.callback_query
    user = query.from_user
    bot = context.bot
    
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
    
    keyboard = [
        [InlineKeyboardButton("• ɢᴇɴᴇʀᴀᴛᴇ sᴇssɪᴏɴ •", callback_data='generate_session')],
        [InlineKeyboardButton("• ʙᴀsɪᴄ ɢᴜɪᴅᴇs •", callback_data='basic_guides')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Delete current message and send new one with image
    await query.message.delete()
    
    image_url = "https://drive.google.com/uc?export=download&id=1lDE4KpTwM9aq9OlNYHEE-lnreUUDgGg-"
    
    try:
        await query.message.reply_photo(
            photo=image_url,
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except:
        await query.message.reply_text(
            message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )

async def start_pyrogram_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Pyrogram session generation."""
    if not update.callback_query:
        return
        
    query = update.callback_query
    user_id = query.from_user.id if query.from_user else 0
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        error_message = "<b>❌ ᴀᴘɪ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ᴇʀʀᴏʀ\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ</b>"
        await edit_message_safely(query, error_message)
        return
    
    # Store session generation type
    session_data[user_id] = {'type': 'pyrogram', 'step': 'phone'}
    
    phone_message = "<b>📱 ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ\n\n🔢 ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ:\n\n📝 ғᴏʀᴍᴀᴛ: +[ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ][ɴᴜᴍʙᴇʀ]\n🔸 ᴇxᴀᴍᴘʟᴇ: +1234567890\n🔸 ᴇxᴀᴍᴘʟᴇ: +91234567890</b>"
    
    await edit_message_safely(query, phone_message)

async def start_telethon_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Telethon session generation."""
    if not update.callback_query:
        return
        
    query = update.callback_query
    user_id = query.from_user.id if query.from_user else 0
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        error_message = "<b>❌ ᴀᴘɪ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ᴇʀʀᴏʀ\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ</b>"
        await edit_message_safely(query, error_message)
        return
    
    # Store session generation type
    session_data[user_id] = {'type': 'telethon', 'step': 'phone'}
    
    phone_message = "<b>📱 ᴛᴇʟᴇᴛʜᴏɴ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ\n\n🔢 ᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ:\n\n📝 ғᴏʀᴍᴀᴛ: +[ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ][ɴᴜᴍʙᴇʀ]\n🔸 ᴇxᴀᴍᴘʟᴇ: +1234567890\n🔸 ᴇxᴀᴍᴘʟᴇ: +91234567890</b>"
    
    await edit_message_safely(query, phone_message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages for session generation."""
    user_id = update.effective_user.id
    
    if user_id not in session_data:
        return
    
    data = session_data[user_id]
    
    if data['step'] == 'phone':
        await handle_phone_number(update, context)
    elif data['step'] == 'otp':
        await handle_otp_code(update, context)
    elif data['step'] == '2fa':
        await handle_2fa_password(update, context)

async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle phone number input with enhanced validation."""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    phone_number = update.message.text.strip() if update.message.text else ""
    
    # Enhanced phone number validation
    is_valid, validation_message = validate_phone_number(phone_number)
    if not is_valid:
        await update.message.reply_text(
            f"<b>❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n\n{validation_message}</b>",
            parse_mode=ParseMode.HTML
        )
        await log_to_group(context, f"Invalid phone number attempt: {phone_number} by user {user_id}", "WARNING")
        return
    
    data = session_data[user_id]
    api_id = int(os.getenv('TELEGRAM_API_ID'))
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    try:
        if data['type'] == 'pyrogram':
            # Use temporary session file
            client = Client(
                f"temp_session_{user_id}", 
                api_id=api_id, 
                api_hash=api_hash,
                in_memory=True
            )
            await client.connect()
            code = await client.send_code(phone_number)
            data['client'] = client
            data['phone_hash'] = code.phone_code_hash
        else:  # telethon
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.connect()
            code = await client.send_code_request(phone_number)
            data['client'] = client
            data['phone_hash'] = code.phone_code_hash
        
        data['phone_number'] = phone_number
        data['step'] = 'otp'
        
        # Enhanced OTP request message with specific format requirement
        otp_message = f"""<b>✅ ᴏᴛᴘ ᴄᴏᴅᴇ sᴇɴᴛ ᴛᴏ {phone_number}

🔢 ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ ᴄᴏᴅᴇ ɪɴ ᴛʜɪs ғᴏʀᴍᴀᴛ:

📝 ʀᴇǫᴜɪʀᴇᴅ ғᴏʀᴍᴀᴛ: 1 2 3 4 5
🔸 sᴘᴀᴄᴇs ʙᴇᴛᴡᴇᴇɴ ᴇᴀᴄʜ ᴅɪɢɪᴛ
🔸 ᴇxᴀᴍᴘʟᴇ: 5 4 3 2 1

⏰ ᴄᴏᴅᴇ ᴇxᴘɪʀᴇs ɪɴ 10 ᴍɪɴᴜᴛᴇs</b>"""
        
        await update.message.reply_text(
            otp_message,
            parse_mode=ParseMode.HTML
        )
        
        # Log successful code sending
        await log_to_group(context, f"OTP sent successfully to {phone_number} for user {user_id}", "SUCCESS")
        
    except (PhoneNumberInvalidError, PhoneNumberInvalid) as e:
        error_msg = "<b>❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n\n📱 ᴛʜɪs ɴᴜᴍʙᴇʀ ɪs ɴᴏᴛ ʀᴇɢɪsᴛᴇʀᴇᴅ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ\n\n🔸 ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɴᴜᴍʙᴇʀ\n🔸 ɪɴᴄʟᴜᴅᴇ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ\n🔸 ᴇxᴀᴍᴘʟᴇ: +1234567890</b>"
        await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
        await log_to_group(context, f"Invalid phone number error for {phone_number} by user {user_id}: {str(e)}", "ERROR")
        # Clean up session data on error
        if user_id in session_data:
            del session_data[user_id]
    except Exception as e:
        logger.error(f"Error sending code to {phone_number}: {str(e)}")
        error_msg = f"<b>❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴏᴛᴘ ᴄᴏᴅᴇ\n\n🔧 ᴛᴇᴄʜɴɪᴄᴀʟ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ\n\n💡 sᴏʟᴜᴛɪᴏɴs:\n• ᴛʀʏ ᴀɢᴀɪɴ ɪɴ 1 ᴍɪɴᴜᴛᴇ\n• ᴄʜᴇᴄᴋ ʏᴏᴜʀ ɪɴᴛᴇʀɴᴇᴛ\n• ᴜsᴇ ᴀ ᴅɪғғᴇʀᴇɴᴛ ɴᴜᴍʙᴇʀ</b>"
        await update.message.reply_text(error_msg, parse_mode=ParseMode.HTML)
        await log_to_group(context, f"Technical error sending OTP to {phone_number} by user {user_id}: {str(e)}", "ERROR")
        # Clean up session data on error
        if user_id in session_data:
            del session_data[user_id]

async def handle_otp_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle OTP code verification with enhanced validation."""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    otp_code = update.message.text.strip() if update.message.text else ""
    
    # Enhanced OTP validation
    is_valid, validation_message = validate_otp_code(otp_code)
    if not is_valid:
        await update.message.reply_text(
            f"<b>❌ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ\n\n{validation_message}</b>",
            parse_mode=ParseMode.HTML
        )
        await log_to_group(context, f"Invalid OTP format attempt: {otp_code} by user {user_id}", "WARNING")
        return
    
    # Convert "1 2 3 4 5" to "12345" for API calls
    otp_for_api = otp_code.replace(" ", "")
    
    if user_id not in session_data:
        await update.message.reply_text(
            "<b>❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ\n\nᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴀɢᴀɪɴ ᴡɪᴛʜ /start</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    data = session_data[user_id]
    
    try:
        if data['type'] == 'pyrogram':
            await data['client'].sign_in(data['phone_number'], data['phone_hash'], otp_for_api)
        else:  # telethon
            await data['client'].sign_in(data['phone_number'], otp_for_api)
        
        # Get session string
        if data['type'] == 'pyrogram':
            session_string = await data['client'].export_session_string()
        else:  # telethon
            session_string = data['client'].session.save()
        
        await data['client'].disconnect()
        
        # Send session string to user
        bot_stats['sessions_generated'] += 1
        
        await update.message.reply_text(
            f"<b>🎉 sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ!\n\n🔒 ʏᴏᴜʀ {data['type'].upper()} sᴇssɪᴏɴ sᴛʀɪɴɢ:\n\n</b><code>{session_string}</code>\n\n<b>⚠️ ᴋᴇᴇᴘ ᴛʜɪs sᴇᴄᴜʀᴇ ᴀɴᴅ ɴᴇᴠᴇʀ sʜᴀʀᴇ ɪᴛ!</b>",
            parse_mode=ParseMode.HTML
        )
        
        # Clean up session data
        del session_data[user_id]
        
    except SessionPasswordNeededError:
        data['step'] = '2fa'
        await update.message.reply_text(
            "<b>🔐 2ғᴀ ᴇɴᴀʙʟᴇᴅ ᴀᴄᴄᴏᴜɴᴛ\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ 2ғᴀ ᴘᴀssᴡᴏʀᴅ</b>",
            parse_mode=ParseMode.HTML
        )
    except PhoneCodeInvalidError:
        await update.message.reply_text(
            "<b>❌ ɪɴᴠᴀʟɪᴅ ᴏᴛᴘ ᴄᴏᴅᴇ\n\nᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ 5-ᴅɪɢɪᴛ ᴄᴏᴅᴇ</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        
        # Check if it's a 2FA error that wasn't caught properly
        if "SESSION_PASSWORD_NEEDED" in str(e):
            data['step'] = '2fa'
            await update.message.reply_text(
                "<b>🔐 2ғᴀ ᴇɴᴀʙʟᴇᴅ ᴀᴄᴄᴏᴜɴᴛ\n\nᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ 2ғᴀ ᴘᴀssᴡᴏʀᴅ</b>",
                parse_mode=ParseMode.HTML
            )
            await log_to_group(context, f"2FA required for user {user_id} (caught in general exception)", "INFO")
        else:
            await update.message.reply_text(
                "<b>❌ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ\n\n🔢 ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴏᴅᴇ ғᴏʀᴍᴀᴛ:\n\n📝 ʀᴇǫᴜɪʀᴇᴅ: 1 2 3 4 5\n🔸 sᴘᴀᴄᴇs ʙᴇᴛᴡᴇᴇɴ ᴇᴀᴄʜ ᴅɪɢɪᴛ</b>",
                parse_mode=ParseMode.HTML
            )
            await log_to_group(context, f"Technical error during OTP verification for user {user_id}: {str(e)}", "ERROR")

async def handle_2fa_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 2FA password verification with enhanced error handling."""
    if not update.effective_user or not update.message:
        return
        
    user_id = update.effective_user.id
    password = update.message.text.strip() if update.message.text else ""
    
    if not password:
        await update.message.reply_text(
            "<b>❌ ᴇᴍᴘᴛʏ ᴘᴀssᴡᴏʀᴅ\n\nᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ 2ғᴀ ᴘᴀssᴡᴏʀᴅ</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if user_id not in session_data:
        await update.message.reply_text(
            "<b>❌ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ\n\nᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴀɢᴀɪɴ ᴡɪᴛʜ /start</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    data = session_data[user_id]
    
    try:
        if data['type'] == 'pyrogram':
            await data['client'].check_password(password)
        else:  # telethon
            await data['client'].sign_in(password=password)
        
        # Get session string
        if data['type'] == 'pyrogram':
            session_string = await data['client'].export_session_string()
        else:  # telethon
            session_string = data['client'].session.save()
        
        await data['client'].disconnect()
        
        # Send session string to user
        bot_stats['sessions_generated'] += 1
        
        await update.message.reply_text(
            f"<b>🎉 sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ!\n\n🔒 ʏᴏᴜʀ {data['type'].upper()} sᴇssɪᴏɴ sᴛʀɪɴɢ:\n\n</b><code>{session_string}</code>\n\n<b>⚠️ ᴋᴇᴇᴘ ᴛʜɪs sᴇᴄᴜʀᴇ ᴀɴᴅ ɴᴇᴠᴇʀ sʜᴀʀᴇ ɪᴛ!</b>",
            parse_mode=ParseMode.HTML
        )
        
        # Clean up session data
        del session_data[user_id]
        
    except Exception as e:
        logger.error(f"Error with 2FA: {e}")
        await update.message.reply_text(
            "<b>❌ ɪɴᴄᴏʀʀᴇᴄᴛ 2ғᴀ ᴘᴀssᴡᴏʀᴅ\n\nᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ</b>",
            parse_mode=ParseMode.HTML
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

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /broadcast command (owner only)."""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("<b>❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴏᴡɴᴇʀ</b>", parse_mode=ParseMode.HTML)
        return
    
    bot_stats['total_commands'] += 1
    
    if not context.args:
        await update.message.reply_text(
            "<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴍᴀɴᴅ\n\nᴜsᴀɢᴇ: /broadcast <message></b>", 
            parse_mode=ParseMode.HTML
        )
        return
    
    message = ' '.join(context.args)
    sent_count = 0
    failed_count = 0
    
    status_msg = await update.message.reply_text(
        "<b>📢 sᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ...</b>", 
        parse_mode=ParseMode.HTML
    )
    
    for user_id in list(bot_stats['total_users']):
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ:\n\n{message}</b>",
                parse_mode=ParseMode.HTML
            )
            sent_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to send broadcast to {user_id}: {e}")
    
    await status_msg.edit_text(
        f"<b>📢 ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!\n\n✅ sᴇɴᴛ: {sent_count}\n❌ ғᴀɪʟᴇᴅ: {failed_count}</b>",
        parse_mode=ParseMode.HTML
    )

def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN environment variable is not set!")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gen", gen_command))
    application.add_handler(CommandHandler("ping", ping_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add message handler for session generation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is starting...")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()