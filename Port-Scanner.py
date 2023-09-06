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
program_version = "1.2.3"
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

# Функция для сканирования портов
def scan_ports(target_ip, start_port, end_port):
    global processed_ports

    try:
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    service_name = get_service_name(port)
                    print(f"Активный порт: {port}, Служба: {service_name}")
                processed_ports += 1
    except KeyboardInterrupt:
        pass

# Функция для получения имени службы по порту
def get_service_name(port):
    try:
        with open("services.txt", "r") as file:
            for line in file:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        port_number = parts[1].split("/")[0]
                        if port_number.isdigit() and int(port_number) == port:
                            return parts[0]
        return "Неизвестно"
    except Exception as e:
        return "Ошибка"

# Функция для логирования результатов сканирования
def log_scan_results(target_ip, open_ports):
    try:
        log_directory = "logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        log_filename = os.path.join(log_directory, f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_scan.log")
        logging.basicConfig(filename=log_filename, level=logging.INFO)
        logging.info(f"Сканирование цели {target_ip}")
        logging.info("Открытые порты:")
        for port in open_ports:
            service_name = get_service_name(port)
            logging.info(f"Порт: {port}, Служба: {service_name}")
        print(f"Лог сохранен в папку: {os.path.abspath(log_filename)}")
    except Exception as e:
        print(f"Ошибка при создании лога: {str(e)}")

if __name__ == "__main__":
    clear_console()  # Очистка консоли при запуске

    check_for_updates()  # Проверяем обновления при запуске

    while True:
        try:
            target = input("Введите IP-адрес для сканирования: ")
            start_port = int(input("Введите начальный порт: "))
            end_port = int(input("Введите конечный порт: "))
            
            # Остальной код для сканирования портов и вывода результатов
            open_ports = []
            print("Идет сканирование...")
            for port in range(start_port, end_port + 1):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        service_name = get_service_name(port)
                        print(f"Активный порт: {port}, Служба: {service_name}")
                        open_ports.append(port)
            
            log_scan_results(target, open_ports)
            
            print("Сканирование завершено.")
            
            choice = input("Введите '0' для продолжения или 'q' для завершения: ")
            if choice.lower() == 'q':
                break
        except Exception as e:
            print(f"Ошибка: {str(e)}")
