import socket
import datetime
import logging
import os
import threading
import concurrent.futures
import sys
import requests
import shutil
import zipfile
import re

# Глобальная переменная для хранения количества обработанных портов
processed_ports = 0

# Пример обновленных переменных
github_repository = "https://github.com/KailJ1/PortScan"
program_name = "Port Scanner"
program_version = "1.2.2"
program_description = "Это программа для сканирования портов."

# Функция для очистки консоли
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

# Функция для загрузки и обновления программы
def download_update():
    try:
        print("Загрузка обновления...")
        update_url = f"{github_repository}/archive/main.zip"
        response = requests.get(update_url)
        if response.status_code == 200:
            with open("update.zip", "wb") as file:
                file.write(response.content)
            print("Обновления успешно загружены. Обновление программы...")
            update_directory = "update_temp"
            with zipfile.ZipFile("update.zip", "r") as zip_ref:
                zip_ref.extractall(update_directory)
            # Заменяем существующие файлы новыми файлами
            for root, dirs, files in os.walk(update_directory):
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(".", file)
                    shutil.copy2(src_file, dest_file)
            print("Программа успешно обновлена.")
            # Удаляем временную папку с обновлениями и архив
            shutil.rmtree(update_directory)
            os.remove("update.zip")
        else:
            print("Не удалось загрузить обновления.")
    except Exception as e:
        print(f"Ошибка при загрузке и обновлении программы: {str(e)}")

# Функция для проверки обновлений
def check_for_updates():
    try:
        clear_console()  # Очистка консоли перед проверкой обновления
        print("Проверка обновлений...")

        update_url = f"{github_repository}/raw/main/news.txt"
        response = requests.get(update_url)

        if response.status_code == 200:
            remote_news = response.text.strip()
            with open("news.txt", "r") as file:
                local_news = file.read().strip()
            if remote_news != local_news:
                # Проверяем версию программы в локальных новостях
                local_version_match = re.search(r"Новая версия: (\d+\.\d+\.\d+)", local_news)
                if local_version_match:
                    local_version = local_version_match.group(1)
                else:
                    local_version = "0.0.0"
                # Проверяем версию программы в удаленных новостях
                remote_version_match = re.search(r"Новая версия: (\d+\.\d+\.\d+)", remote_news)
                if remote_version_match:
                    remote_version = remote_version_match.group(1)
                else:
                    remote_version = "0.0.0"
                # Сравниваем версии и предлагаем обновление только при несоответствии версий
                if remote_version != local_version:
                    print("Доступно обновление. Желаете скачать обновление?")
                    choice = input("Введите '1' для скачивания обновления или '2' для продолжения без обновления: ")
                    if choice == '1':
                        download_update()
                else:
                    print("У вас уже новая версия.")  # Добавляем эту строку
            else:
                print("У вас установлена последняя версия.")
        else:
            print("Не удалось проверить обновления.")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")

# Остальной код остается без изменений
# ...

if __name__ == "__main__":
    clear_console()  # Очистка консоли при запуске

    check_for_updates()  # Проверяем обновления при запуске

    while True:
        # Остальной код остается без изменений
        # ...
