import cv2
from deepface import DeepFace
import telebot
import threading
import json
import os
import time
from PyQt5 import QtWidgets, QtGui

# Функция для настройки конфигурации
def setup():
    token = input("Введите Telegram Token: ").strip()
    chat_id = input("Введите Telegram Chat ID: ").strip()
    config = {"TOKEN": token, "CHAT_ID": chat_id, "INTERVAL": 15}  # Интервал по умолчанию
    with open('config.json', 'w') as f:
        json.dump(config, f)
    print("Настройка завершена!")

# Загрузка конфигурации
def load_config():
    if not os.path.exists('config.json'):
        setup()
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()
TOKEN = config['TOKEN']
CHAT_ID = config['CHAT_ID']
INTERVAL = config.get('INTERVAL', 15)

bot = telebot.TeleBot(TOKEN)
detection_active = False

def detect_emotions():
    global detection_active
    detection_active = True
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        bot.send_message(CHAT_ID, "❌ Ошибка доступа к камере")
        detection_active = False
        return
    prev_emotion = None
    while detection_active:
        time.sleep(INTERVAL)
        ret, frame = cap.read()
        if not ret:
            bot.send_message(CHAT_ID, "❌ Ошибка захвата кадра")
            break
        try:
            analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emotion = analysis[0]['dominant_emotion']
            emotion_probability = analysis[0]['emotion'][emotion]
            if emotion != prev_emotion:
                photo_path = "detected_emotion.jpg"
                cv2.imwrite(photo_path, frame)
                bot.send_message(CHAT_ID, f"👤 Эмоция: {emotion} ({emotion_probability:.2f}%)")
                with open(photo_path, 'rb') as photo:
                    bot.send_photo(CHAT_ID, photo)
                prev_emotion = emotion
        except Exception as e:
            bot.send_message(CHAT_ID, f"❌ Ошибка анализа: {e}")
    cap.release()
    detection_active = False

class EmotionBotUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Emotion Detection Bot')
        self.setGeometry(100, 100, 400, 300)
        layout = QtWidgets.QVBoxLayout()

        self.token_input = QtWidgets.QLineEdit(self)
        self.token_input.setPlaceholderText("Введите Telegram Token")
        self.token_input.setText(TOKEN)
        layout.addWidget(self.token_input)

        self.chat_id_input = QtWidgets.QLineEdit(self)
        self.chat_id_input.setPlaceholderText("Введите Telegram Chat ID")
        self.chat_id_input.setText(CHAT_ID)
        layout.addWidget(self.chat_id_input)

        self.interval_input = QtWidgets.QSpinBox(self)
        self.interval_input.setRange(5, 60)
        self.interval_input.setValue(INTERVAL)
        self.interval_input.setSuffix(" сек")
        layout.addWidget(self.interval_input)

        self.start_btn = QtWidgets.QPushButton("Старт", self)
        self.start_btn.clicked.connect(self.start_analysis)
        layout.addWidget(self.start_btn)

        self.stop_btn = QtWidgets.QPushButton("Стоп", self)
        self.stop_btn.clicked.connect(self.stop_analysis)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

    def start_analysis(self):
        global TOKEN, CHAT_ID, INTERVAL, detection_active
        TOKEN = self.token_input.text()
        CHAT_ID = self.chat_id_input.text()
        INTERVAL = self.interval_input.value()
        config.update({"TOKEN": TOKEN, "CHAT_ID": CHAT_ID, "INTERVAL": INTERVAL})
        with open('config.json', 'w') as f:
            json.dump(config, f)
        if not detection_active:
            threading.Thread(target=detect_emotions).start()

    def stop_analysis(self):
        global detection_active
        detection_active = False

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = EmotionBotUI()
    window.show()
    app.exec_()
