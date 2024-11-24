from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from yt_dlp import YoutubeDL
import os

        # Ваш Telegram Bot Token
API_TOKEN = "7875828743:AAHCLeXP6j9zEEY2fc3GG_yyeIhHw9P6e_s"

        # Ініціалізація об'єкта Bot і Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

        # Функція для пошуку 10 схожих аудіофайлів
def search_audio(search_query):
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
            }

            results = []
            with YoutubeDL(ydl_opts) as ydl:
                # Пошук до 10 результатів
                info = ydl.extract_info(f"ytsearch10:{search_query}", download=False)
                for entry in info['entries']:
                    results.append({'title': entry['title'], 'webpage_url': entry['webpage_url'], 'uploader': entry['uploader']})
            return results

        # Функція для завантаження обраної пісні
def download_audio(url):
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                filepath = f"downloads/{title}.mp3"
                return filepath, title

        # Команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
            await message.reply("👋 Привіт! Надішли назву пісні або виконавця, щоб отримати список результатів.")

        # Обробка текстового запиту
@dp.message_handler()
async def handle_message(message: types.Message):
            query = message.text
            results = search_audio(query)

            if not results:
                await message.reply("❌ Не вдалося знайти пісні за вашим запитом.")
                return

            # Формування кнопок для результатів
            keyboard = types.InlineKeyboardMarkup()
            for result in results:
                button = types.InlineKeyboardButton(
                    text=f"{result['title']} (виконавець: {result['uploader']})",
                    callback_data=result['webpage_url']
                )
                keyboard.add(button)

            await message.reply("🔎 Знайдені результати. Оберіть пісню для завантаження:", reply_markup=keyboard)

        # Обробка натискання кнопки для вибору пісні
@dp.callback_query_handler(lambda callback_query: True)
async def handle_choice(callback_query: types.CallbackQuery):
            url = callback_query.data
            await callback_query.message.reply("🔄 Завантажую вибрану пісню, зачекайте...")

            try:
                # Завантаження вибраної пісні
                filepath, title = download_audio(url)

                # Надсилання пісні користувачеві
                with open(filepath, 'rb') as audio:
                    await callback_query.message.reply_audio(audio, caption=f"🎵 {title}")

                # Видалення файлу після надсилання
                os.remove(filepath)
            except Exception as e:
                await callback_query.message.reply(f"❌ Сталася помилка: {e}")

        # Запуск бота
if __name__ == "__main__":
            if not os.path.exists("downloads"):
                os.mkdir("downloads")  # Створення папки для збереження аудіо
            executor.start_polling(dp, skip_updates=True)