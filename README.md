# MoodleJKU-AutoLogin

[English version below / Англійська версія нижче]

## Українська версія

MoodleJKU-AutoLogin - це Python-скрипт для автоматичного входу в систему Moodle Університету Йоганнеса Кеплера (JKU). Цей інструмент спрощує процес автентифікації, дозволяючи швидко отримати доступ до курсів та матеріалів Moodle.

### Особливості

- Автоматичний вхід в систему Moodle JKU
- Підтримка автентифікації через Shibboleth
- Безпечне зберігання облікових даних
- Детальне логування процесу входу
- Можливість швидкого доступу до конкретного курсу

### Вимоги

- Python 3.6+
- requests
- beautifulsoup4
- urllib3

### Встановлення

1. Клонуйте репозиторій:
   ```
   git clone https://github.com/your-username/MoodleJKU-AutoLogin.git
   ```

2. Перейдіть до каталогу проекту:
   ```
   cd MoodleJKU-AutoLogin
   ```

3. Встановіть необхідні залежності:
   ```
   pip install -r requirements.txt
   ```

### Використання

Ви можете запустити скрипт двома способами:

1. Передача облікових даних через аргументи командного рядка:
   ```
   python moodlejku_autologin.py --username YOUR_USERNAME --password YOUR_PASSWORD
   ```

2. Використання змінних середовища:
   ```
   export MOODLE_USERNAME=YOUR_USERNAME
   export MOODLE_PASSWORD=YOUR_PASSWORD
   python moodlejku_autologin.py
   ```

### Безпека

Будь ласка, не зберігайте ваші облікові дані у відкритому вигляді в коді. Використовуйте змінні середовища або передавайте їх через аргументи командного рядка.

### Внесок

Якщо у вас є ідеї щодо покращення цього проекту, будь ласка, створіть issue або надішліть pull request.

### Ліцензія

Цей проект ліцензовано під MIT License - дивіться файл [LICENSE](LICENSE) для деталей.

### Відмова від відповідальності

Цей скрипт призначений виключно для особистого використання. Автор не несе відповідальності за будь-яке неправомірне використання або порушення умов використання системи Moodle JKU.

---

## English version

MoodleJKU-AutoLogin is a Python script for automatic login to the Moodle system of Johannes Kepler University (JKU). This tool simplifies the authentication process, allowing quick access to Moodle courses and materials.

### Features

- Automatic login to the JKU Moodle system
- Support for Shibboleth authentication
- Secure credential storage
- Detailed logging of the login process
- Ability to quickly access a specific course

### Requirements

- Python 3.6+
- requests
- beautifulsoup4
- urllib3

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/MoodleJKU-AutoLogin.git
   ```

2. Navigate to the project directory:
   ```
   cd MoodleJKU-AutoLogin
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Usage

You can run the script in two ways:

1. Passing credentials via command-line arguments:
   ```
   python moodlejku_autologin.py --username YOUR_USERNAME --password YOUR_PASSWORD
   ```

2. Using environment variables:
   ```
   export MOODLE_USERNAME=YOUR_USERNAME
   export MOODLE_PASSWORD=YOUR_PASSWORD
   python moodlejku_autologin.py
   ```

### Security

Please do not store your credentials in plain text in the code. Use environment variables or pass them through command-line arguments.

### Contributing

If you have ideas for improving this project, please create an issue or send a pull request.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Disclaimer

This script is intended for personal use only. The author is not responsible for any misuse or violation of the terms of use of the JKU Moodle system.
