import socket
import datetime
import logging
import os
import requests

# Глобальная переменная для хранения количества обработанных портов
processed_ports = 0

# Функция для очистки консоли
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

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

# Функция для проверки обновлений
def check_for_updates():
    try:
        clear_console()  # Очистка консоли перед проверкой обновления
        print("Проверка обновлений...")
        
        # Загрузка версии и изменений из файла Update.txt на GitHub
        update_url = "https://raw.githubusercontent.com/KailJ1/PortScan/main/Update.txt"
        response = requests.get(update_url)
        
        if response.status_code == 200:
            remote_data = response.text.strip().split("\n")
            remote_version = remote_data[0].split(": ")[1].strip()
            
            with open("Update.txt", "r") as local_file:
                local_data = local_file.read().strip().split("\n")
                local_version = local_data[0].split(": ")[1].strip()
            
            # Сравнение версий и вывод информации
            if remote_version > local_version:
                print(f"Доступна новая версия {remote_version}.")
                print("\n".join(remote_data[1:]))
                choice = input("Введите '1' для скачивания обновления или '2' для продолжения без обновления: ")
                if choice == '1':
                    download_update()
            else:
                print("У вас установлена последняя версия.")
        else:
            print("Не удалось проверить обновления.")
    except Exception as e:
        print(f"Ошибка при проверке обновлений: {str(e)}")

# Функция для скачивания обновления
def download_update():
    try:
        update_url = "https://github.com/KailJ1/PortScan/archive/main.zip"
        response = requests.get(update_url)
        if response.status_code == 200:
            with open("update.zip", "wb") as zip_file:
                zip_file.write(response.content)
            print("Обновление успешно скачано. Запустите программу после распаковки.")
        else:
            print("Не удалось скачать обновление.")
    except Exception as e:
        print(f"Ошибка при скачивании обновления: {str(e)}")

if __name__ == "__main__":
    clear_console()  # Очистка консоли при запуске

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
