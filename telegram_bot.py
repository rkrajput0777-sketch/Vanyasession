#!/usr/bin/env python3
import logging
import os
import time
import asyncio
import tempfile
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from telegram.constants import ParseMode
from pyrogram import Client
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
bot_stats = {
    'start_time': time.time(),
    'total_users': set(),
    'sessions_generated': 0,
    'total_commands': 0
}

# Session generation data storage
session_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
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
• ᴡɪᴅᴇʟʏ ᴜsᴇᴅ</b>"""
        
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
        await start_pyrogram_session(update, context)
    
    elif query.data == 'telethon_gen':
        await start_telethon_session(update, context)
    
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
    query = update.callback_query
    user_id = query.from_user.id
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        await query.edit_message_text(
            "<b>❌ ᴀᴘɪ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ᴇʀʀᴏʀ\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Store session generation type
    session_data[user_id] = {'type': 'pyrogram', 'step': 'phone'}
    
    await query.edit_message_text(
        "<b>📱 ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ\nᴇxᴀᴍᴘʟᴇ: +1234567890</b>",
        parse_mode=ParseMode.HTML
    )

async def start_telethon_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Telethon session generation."""
    query = update.callback_query
    user_id = query.from_user.id
    
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        await query.edit_message_text(
            "<b>❌ ᴀᴘɪ ᴄᴏɴғɪɢᴜʀᴀᴛɪᴏɴ ᴇʀʀᴏʀ\n\nᴘʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Store session generation type
    session_data[user_id] = {'type': 'telethon', 'step': 'phone'}
    
    await query.edit_message_text(
        "<b>📱 ᴛᴇʟᴇᴛʜᴏɴ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛɪᴏɴ\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ\nᴇxᴀᴍᴘʟᴇ: +1234567890</b>",
        parse_mode=ParseMode.HTML
    )

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
    """Handle phone number input."""
    user_id = update.effective_user.id
    phone_number = update.message.text.strip()
    
    data = session_data[user_id]
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    try:
        if data['type'] == 'pyrogram':
            client = Client(f"session_{user_id}", api_id=api_id, api_hash=api_hash)
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
        
        await update.message.reply_text(
            f"<b>✅ ᴏᴛᴘ ᴄᴏᴅᴇ sᴇɴᴛ ᴛᴏ {phone_number}\n\nᴘʟᴇᴀsᴇ sᴇɴᴅ ᴛʜᴇ 5-ᴅɪɢɪᴛ ᴄᴏᴅᴇ ʏᴏᴜ ʀᴇᴄᴇɪᴠᴇᴅ</b>",
            parse_mode=ParseMode.HTML
        )
        
    except PhoneNumberInvalidError:
        await update.message.reply_text(
            "<b>❌ ɪɴᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n\nᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending code: {e}")
        await update.message.reply_text(
            "<b>❌ ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴏᴛᴘ ᴄᴏᴅᴇ\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</b>",
            parse_mode=ParseMode.HTML
        )

async def handle_otp_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle OTP code verification."""
    user_id = update.effective_user.id
    otp_code = update.message.text.strip()
    
    data = session_data[user_id]
    
    try:
        if data['type'] == 'pyrogram':
            await data['client'].sign_in(data['phone_number'], data['phone_hash'], otp_code)
        else:  # telethon
            await data['client'].sign_in(data['phone_number'], otp_code)
        
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
        await update.message.reply_text(
            "<b>❌ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴏʀ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴏᴅᴇ</b>",
            parse_mode=ParseMode.HTML
        )

async def handle_2fa_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 2FA password verification."""
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
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
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add message handler for session generation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot is starting...")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()