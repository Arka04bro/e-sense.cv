import cv2
import requests
from aiogram import Bot, Dispatcher, types
import asyncio

# Токен твоего бота
TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Функция для отправки сообщения в Telegram асинхронно
async def send_telegram_message(message):
    chat_id = "USER_CHAT_ID"  # ID чата, куда будут отправляться сообщения
    await bot.send_message(chat_id, message)

# Функция для отправки изображения на бэкенд для получения эмоции
def get_emotion_from_backend(image):
    url = "http://your-backend-url.com/analyze_emotion"  # URL твоего API
    _, img_encoded = cv2.imencode('.jpg', image)  # Кодируем изображение в формат JPEG
    files = {'image': img_encoded.tobytes()}  # Отправляем файл как байты
    response = requests.post(url, files=files)  # Отправляем POST запрос
    if response.status_code == 200:
        return response.json()  # Ожидаем, что в ответе будет эмоция
    else:
        print("Error:", response.status_code)
        return None

# Основная асинхронная функция для анализа эмоций через камеру и отправки в Telegram
async def detect_emotions():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to capture video frame.")
            break

        # Отправка кадра на сервер для получения эмоции
        emotion_data = get_emotion_from_backend(frame)

        if emotion_data:
            emotion = emotion_data.get('dominant_emotion', 'Unknown')  # Извлекаем эмоцию
            print(f"Detected Emotion: {emotion}")

            # Отправка сообщения в Telegram асинхронно
            await send_telegram_message(f"Detected Emotion: {emotion}")

        # Отображение видео с текущим кадром
        cv2.imshow('Emotion Detection', frame)

        # Закрытие окна по нажатию 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Запуск асинхронной работы с aiogram
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(detect_emotions())
