import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from deep_translator import GoogleTranslator

# Fetch the Telegram API token from environment variables
API_TOKEN = os.environ.get('BOT_TOKEN')

if not API_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

bot = telebot.TeleBot(API_TOKEN)

# User language preferences storage (in-memory)
user_target_langs = {}

# Supported target languages
LANGUAGES = {
    "English 🇬🇧": "en",
    "Spanish 🇪🇸": "es",
    "French 🇫🇷": "fr",
    "German 🇩🇪": "de",
    "Chinese 🇨🇳": "zh-CN",
    "Arabic 🇸🇦": "ar",
    "Russian 🇷🇺": "ru",
    "Japanese 🇯🇵": "ja"
}

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(name, callback_data=f"setlang_{code}")
        for name, code in LANGUAGES.items()
    ]
    keyboard.add(*buttons)
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Welcome to SB Service 24h!*\n\n"
        "I am your instant 24/7 translation assistant.\n"
        "Send me any text, and I will automatically detect the language and translate it for you.\n\n"
        "⚙️ *Current Default Target:* English\n"
        "🌐 Use /setlang to change your target language."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "ℹ️ *SB Service 24h Help*\n\n"
        "• Send any plain text message to translate.\n"
        "• Use /setlang to pick your desired translation language.\n"
        "• Use /start to reset or see the welcome message."
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['setlang'])
def choose_language(message):
    bot.send_message(
        message.chat.id,
        "🌐 *Please select your target translation language:*",
        reply_markup=get_language_keyboard(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('setlang_'))
def set_language_callback(call):
    lang_code = call.data.split('_')[1]
    user_target_langs[call.message.chat.id] = lang_code
    
    # Get the display name for the selected language
    lang_name = [name for name, code in LANGUAGES.items() if code == lang_code][0]
    
    bot.answer_callback_query(call.id, f"Language set to {lang_name}")
    bot.edit_message_text(
        f"✅ Target language successfully set to: *{lang_name}*\n\nSend any message now to translate!",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True, content_types=['text'])
def translate_message(message):
    chat_id = message.chat.id
    target_lang = user_target_langs.get(chat_id, 'en')  # Default target is English
    
    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(message.text)
        bot.reply_to(message, f"🔤 *Translation:*\n{translated_text}", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "❌ An error occurred during translation. Please try again.")

if __name__ == "__main__":
    # Register bot commands menu in Telegram chat interface
    bot.set_my_commands([
        BotCommand("start", "Start the translation bot"),
        BotCommand("setlang", "Choose target translation language"),
        BotCommand("help", "Get help using the bot")
    ])
    
    # Clear active webhook without arguments
    bot.remove_webhook()
    
    print("SB Service 24h Bot is active and running...")
    bot.infinity_polling()
