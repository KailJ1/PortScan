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

# Глобальная переменная для хранения количества обработанных портов
processed_ports = 0

# Пример обновленных переменных
github_repository = "https://github.com/KailJ1/PortScan"
program_name = "Port Scanner"
program_version = "1.5"
program_description = "Это программа для сканирования портов."

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
        print("Проверка обновлений...")
        update_url = f"{github_repository}/raw/main/news.txt"
        response = requests.get(update_url)
        if response.status_code == 200:
            remote_news = response.text.strip()
            with open("news.txt", "r") as file:
                local_news = file.read().strip()
            if remote_news != local_news:
                print("Доступно обновление. Желаете скачать обновление?")
                choice = input("Введите '1' для скачивания обновления или '2' для продолжения без обновления: ")
                if choice == '1':
                    download_update()
            else:
                print("У вас установлена последняя версия.")
        else:
            print("Не удалось проверить обновления.")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")

# Остальной код остается без изменений
# ...

if __name__ == "__main__":
    check_for_updates()  # Проверяем обновления при запуске

    while True:
        os.system("cls" if os.name == "nt" else "clear")  # Очистка консоли при запуске

        target = input("Введите IP-адрес или доменное имя для сканирования: ")
        
        try:
            # Пытаемся разрешить доменное имя в IP-адрес
            target_ip = socket.gethostbyname(target)
            print(f"IP-адрес для сканирования: {target_ip}")
        except socket.gaierror:
            print(f"Не удалось разрешить доменное имя: {target}")
            sys.exit(1)
        
        start_port = int(input("Введите начальный порт для сканирования (-1 для стандартных и 25560-25580): "))

        if start_port != -1:
            end_port = int(input("Введите конечный порт для сканирования: "))
        else:
            end_port = start_port  # Если указан порт -1, конечный порт также равен -1

        print("Идёт сканирование...")  # Добавляем сообщение о начале сканирования

        open_ports = scan_ports(target_ip, start_port, end_port)

        if open_ports:
            print("Активные порты:")
            for port in open_ports:
                service_name = get_service_name(port)
                print(f"IP: {target_ip}, Port: {port}, Service: {service_name}")

            log_scan_results(target_ip, open_ports)
            print(f"Лог сохранён в папку: {os.path.abspath(log_directory)}/{log_filename}")
        else:
            print("На заданном IP нет активных портов.")
        
        continue_input = input("Введите '0' для продолжения или любой другой символ для завершения: ")
        if continue_input != '0':
            break
