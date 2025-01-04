from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox,
                             QTabWidget, QProgressBar, QComboBox, QStackedWidget, QFileDialog)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap, QImage, QBrush
import sys
import threading
import cv2
from deepface import DeepFace
import speech_recognition as sr
import pywhatkit as kit
import time

# List of bad words
bad_words = [
    'дурак', 'идиот', 'тупой', 'мразь', 'глупый', 'сволочь',
    'ублюдок', 'негодяй', 'козел', 'долбоеб', 'пидорас', 'сучонок','чорт','хуй','в пизду','твою мать','сука','в жопу','кал лошадиный','говно вонючее'
    'ебать тебя в сраку' , 'злоебучая пиздопроёбина' , 'сиська' , 'урод ебучий','член импотента','все бабы дуры, а мужики импотенты' , 'тварь позорная',
    'минеты делать','узкоглазая шлюха','малолетка недоёбанная','малолетка','я хуею','затычка в жопе'
]


# Function to send message via WhatsApp
def send_message(message, phone_number):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    full_message = f"{current_time} - {message}"
    kit.sendwhatmsg_instantly(phone_number, full_message, 10)


# Function for listening and detecting bad words
def listen_and_detect(phone_number):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=None)
                text = recognizer.recognize_google(audio, language="ru-RU")
                if any(word in text.lower() for word in bad_words):
                    send_message("Bad word detected!", phone_number)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                send_message(f"Google Speech Recognition error: {e}", phone_number)


# Function for detecting emotion
def detect_emotion(phone_number):
    cup = cv2.VideoCapture(0)
    while True:
        ret, frame = cup.read()
        if not ret:
            continue
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        try:
            vn = DeepFace.analyze(rgb_frame, actions=['emotion'])
            if 'emotion' in vn[0]:
                emotion = vn[0]['emotion']
                if emotion['angry'] > 10:
                    send_message('You seem angry', phone_number)
        except Exception as e:
            print(f"Error in emotion detection: {e}")
    cup.release()
    cv2.destroyAllWindows()


# Dictionaries for languages
translations = {
    'en': {
        'phone_number': "Enter phone number:",
        'camera_checkbox': "Enable camera",
        'start_button': "Start Monitoring",
        'donate_info': "You can donate for the development of the project.\nKaspi-gold: 87717693741\nCard: 4400022481633",
        'developers_info': "Main Developer: Arkat Khasanov\nPhone: 87717693741\nInstagram: @arkkatt\nCEO: Nurbakyt Karazhakov\nPhone: +7 702 934 7121",
        'about_info': "The project analyzes emotions and detects foul language and aggressive emotions.",
        'version_info': "Your version: E-sense-2.0",
        'theme_label': "Choose Theme:",
        'language_label': "Choose Language:",
        'background_image_button': "Change Background Image"
    },
    'ru': {
        'phone_number': "Введите номер телефона:",
        'camera_checkbox': "Включить камеру",
        'start_button': "Начать мониторинг",
        'donate_info': "Вы можете пожертвовать деньги на развитие проекта.\nKaspi-gold: 87717693741\nНомер карты: 4400022481633",
        'developers_info': "Главный разработчик: Аркат Хасанов\nТелефон: 87717693741\nInstagram: @arkkatt\nCEO: Нурбакыт Каражаков\nТелефон: +7 702 934 7121",
        'about_info': "Проект анализирует эмоции и выявляет нецензурную лексику и агрессивные эмоции.",
        'version_info': "Ваша версия: E-sense-2.0",
        'theme_label': "Выберите тему:",
        'language_label': "Выберите язык:",
        'background_image_button': "Изменить фон"
    },
    'kk': {
        'phone_number': "Телефон нөмірін енгізіңіз:",
        'camera_checkbox': "Камераны қосу",
        'start_button': "Мониторингті бастау",
        'donate_info': "Жобаны дамыту үшін ақша аудара аласыз.\nKaspi-gold: 87717693741\nКарта нөмірі: 4400022481633",
        'developers_info': "Негізгі әзірлеуші: Аркат Хасанов\nТелефон: 87717693741\nInstagram: @arkkatt\nCEO: Нурбакыт Каражаков\nТелефон: +7 702 934 7121",
        'about_info': "Жоба эмоцияларды талдап, бейәдеп сөздер мен агрессивті эмоцияларды анықтайды.",
        'version_info': "Сіздің нұсқаңыз: E-sense-2.0",
        'theme_label': "Тақырыпты таңдаңыз:",
        'language_label': "Тілді таңдаңыз:",
        'background_image_button': "Фонды өзгерту"
    }
}


# Main App class
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_language = 'en'  # Default language
        self.initUI()

    def initUI(self):
        # Font settings
        font = QFont("Roboto", 30)

        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(font)

        # Create all tabs
        self.main_tab = QWidget()
        self.create_main_tab(font)

        self.donation_tab = QWidget()
        self.create_donation_tab(font)

        self.developers_tab = QWidget()
        self.create_developers_tab(font)

        self.about_tab = QWidget()
        self.create_about_tab(font)

        self.version_tab = QWidget()
        self.create_version_tab(font)

        self.settings_tab = QWidget()
        self.create_settings_tab(font)

        # Add tabs to the widget
        self.tabs.addTab(self.main_tab, "Monitoring")
        self.tabs.addTab(self.donation_tab, "Donate")
        self.tabs.addTab(self.developers_tab, "About Developers")
        self.tabs.addTab(self.about_tab, "About Project")
        self.tabs.addTab(self.version_tab, "Version Info")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.setWindowTitle("Parental Control")
        self.resize(1090, 1020)  # Set window size to 1090x1020

        # Now set the theme after all components are initialized
        self.setLightMode()  # Default to light mode
        self.update_translations()

    def create_main_tab(self, font):
        layout = QVBoxLayout()
        self.phone_label = QLabel()
        self.phone_label.setFont(font)
        self.phone_input = QLineEdit(self)
        self.phone_input.setFont(font)
        self.camera_checkbox = QCheckBox()
        self.camera_checkbox.setFont(font)
        self.start_button = QPushButton(self)
        self.start_button.setFont(font)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        layout.addWidget(self.phone_label)
        layout.addWidget(self.phone_input)
        layout.addWidget(self.camera_checkbox)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        self.main_tab.setLayout(layout)

        self.start_button.clicked.connect(self.start_monitoring)

    def create_donation_tab(self, font):
        layout = QVBoxLayout()
        self.donation_info = QLabel()
        self.donation_info.setFont(font)
        layout.addWidget(self.donation_info)
        self.donation_tab.setLayout(layout)

    def create_developers_tab(self, font):
        layout = QVBoxLayout()
        self.developers_info = QLabel()
        self.developers_info.setFont(font)
        layout.addWidget(self.developers_info)
        self.developers_tab.setLayout(layout)

    def create_about_tab(self, font):
        layout = QVBoxLayout()
        self.about_info = QLabel()
        self.about_info.setFont(font)
        layout.addWidget(self.about_info)
        self.about_tab.setLayout(layout)

    def create_version_tab(self, font):
        layout = QVBoxLayout()
        self.version_info = QLabel()
        self.version_info.setFont(font)
        layout.addWidget(self.version_info)
        self.version_tab.setLayout(layout)

    def create_settings_tab(self, font):
        layout = QVBoxLayout()

        # Light/Dark mode toggle
        self.theme_label = QLabel()
        self.theme_label.setFont(font)
        self.theme_combobox = QComboBox()
        self.theme_combobox.setFont(font)
        self.theme_combobox.addItems(["Light Mode", "Dark Mode"])
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)

        # Language selection
        self.language_label = QLabel()
        self.language_label.setFont(font)
        self.language_combobox = QComboBox()
        self.language_combobox.setFont(font)
        self.language_combobox.addItems(["English", "Russian", "Kazakh"])
        self.language_combobox.currentIndexChanged.connect(self.change_language)

        # Background image button
        self.background_image_button = QPushButton()
        self.background_image_button.setFont(font)
        self.background_image_button.setText("Change Background Image")
        self.background_image_button.clicked.connect(self.change_background_image)

        layout.addWidget(self.theme_label)
        layout.addWidget(self.theme_combobox)
        layout.addWidget(self.language_label)
        layout.addWidget(self.language_combobox)
        layout.addWidget(self.background_image_button)
        self.settings_tab.setLayout(layout)

    def start_monitoring(self):
        phone_number = self.phone_input.text()
        if phone_number:
            if self.camera_checkbox.isChecked():
                # Start emotion detection in a new thread
                threading.Thread(target=detect_emotion, args=(phone_number,), daemon=True).start()
            # Start speech recognition in a new thread
            threading.Thread(target=listen_and_detect, args=(phone_number,), daemon=True).start()
            self.update_progress_bar()

    def update_progress_bar(self):
        self.progress_bar.setValue(50)  # Example progress

    def change_theme(self, index):
        if index == 0:  # Light Mode
            self.setLightMode()
        else:  # Dark Mode
            self.setDarkMode()

    def setLightMode(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFF0F5;  /* Lightest pink */
                color: black;
            }
            QTabWidget::pane { /* The tab widget frame */
                background-color: #FFD1DA; /* Light soft pink */
                border: 1px solid #FBA1B7;
            }
            QTabBar::tab {
                background-color: #FFD1DA; /* Tab color */
                color: black;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background-color: #FBA1B7; /* Selected tab color */
                color: white;
            }
            QPushButton {
                background-color: #FFD1DA;
                border: 2px solid #FBA1B7;
                border-radius: 10px;
                color: black;
            }
            QPushButton:hover {
                background-color: #FBA1B7;
                color: white;
            }
            QLabel {
                color: #FBA1B7;  /* Text color similar to pink */
            }
        """)
        self.set_background_image("C:/Users/Admin/Downloads/den-semi.jpg")  # Optionally, use a background image

    # Set the default background image

    def setDarkMode(self):
        self.setStyleSheet("background-color: black; color: white;")
        self.theme_label.setText("Тақырыпты таңдаңыз:")
        self.language_label.setText("Тілді таңдаңыз:")
        self.set_background_image("C:/Users/Admin/Downloads/den-semi.jpg")  # Set the default background image

    def change_language(self, index):
        languages = ['en', 'ru', 'kk']
        self.current_language = languages[index]
        self.update_translations()

    def update_translations(self):
        lang = translations[self.current_language]
        self.phone_label.setText(lang['phone_number'])
        self.camera_checkbox.setText(lang['camera_checkbox'])
        self.start_button.setText(lang['start_button'])
        self.donation_info.setText(lang['donate_info'])
        self.developers_info.setText(lang['developers_info'])
        self.about_info.setText(lang['about_info'])
        self.version_info.setText(lang['version_info'])
        self.theme_label.setText(lang['theme_label'])
        self.language_label.setText(lang['language_label'])
        self.background_image_button.setText(lang['background_image_button'])

    def set_background_image(self, image_path):
        if image_path:
            # Load the image and set it as the background
            pixmap = QPixmap(image_path)
            palette = self.palette()
            palette.setBrush(QPalette.Background, QBrush(pixmap))
            self.setPalette(palette)
        else:
            # Reset to default background
            self.setStyleSheet("background-color: white;")

    def change_background_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Background Image", "", "Images (*.png *.jpg *.bmp)",
                                                   options=options)
        if file_path:
            self.set_background_image(file_path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
