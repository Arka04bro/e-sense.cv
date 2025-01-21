import cv2
from deepface import DeepFace
import telebot
import threading
import json
import os
def setup():
    print("Добро пожаловать в настройку Emotion Detection Bot!")
    token = input("Введите ваш токен бота (полученный от @BotFather): ").strip()
    chat_id = input("Введите ваш chat_id (узнать его можно у @userinfobot в Telegram): ").strip()
    config = {
        "TOKEN": token,
        "CHAT_ID": chat_id
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)
    
    print("Настройка завершена!")
def load_config():
    if not os.path.exists('config.json'):
        setup()
    
    with open('config.json', 'r') as f:
        return json.load(f)
config = load_config()
TOKEN = config['TOKEN']
CHAT_ID = config['CHAT_ID']

bot = telebot.TeleBot(TOKEN)
detection_active = False

# Функция для анализа эмоций
def detect_emotions():
    global detection_active
    detection_active = True
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Ошибка доступа к камере")
        bot.send_message(CHAT_ID, "❌ Ошибка доступа к камере")
        detection_active = False
        return
    
    prev_emotion = None
    while detection_active:
        ret, frame = cap.read()
        if not ret:
            print("❌ Ошибка захвата кадра")
            bot.send_message(CHAT_ID, "❌ Ошибка захвата кадра")
            break
        
        try:
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = analysis[0]['dominant_emotion'] if isinstance(analysis, list) else analysis['dominant_emotion']
            
            if emotion != prev_emotion:
                print(f"Обнаружена эмоция: {emotion}")
                bot.send_message(CHAT_ID, f"👤 Эмоция: {emotion}")
                prev_emotion = emotion
                
            cv2.imshow('Emotion Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                detection_active = False
                break
                
        except Exception as e:
            print(f"Ошибка анализа: {e}")
            bot.send_message(CHAT_ID, f"❌ Ошибка анализа: {e}")
    
    cap.release()
    cv2.destroyAllWindows()
    detection_active = False
    print("Анализ эмоций завершен.")
@bot.message_handler(commands=['start'])
def start(message):
    global detection_active
    if not detection_active:
        print("Запуск потока для анализа эмоций...")
        threading.Thread(target=detect_emotions).start()
        bot.reply_to(message, "🔍 Анализ эмоций запущен!")
    else:
        bot.reply_to(message, "⚠️ Анализ уже выполняется")
@bot.message_handler(commands=['stop'])
def stop(message):
    global detection_active
    detection_active = False
    bot.reply_to(message, "⏹ Анализ остановлен")
if __name__ == "__main__":
    print("Бот запущен. Используйте команды /start и /stop в Telegram.")
    bot.polling(none_stop=True)
