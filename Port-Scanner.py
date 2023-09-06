import socket
import os
import datetime
import logging
import subprocess
import zipfile
import shutil
import requests

# Очистка консоли
def clear_console():
    if os.name == 'posix':
        subprocess.call('clear', shell=True)
    elif os.name == 'nt':
        subprocess.call('cls', shell=True)

# Функция для сканирования портов
def scan_ports(target_ip, start_port, end_port):
    global processed_ports

    try:
        if start_port == -1:
            start_port = 1
            end_port = 1024  # Стандартные порты

            # Словарь с информацией о стандартных портах и их службах
            standard_ports = {
                21: "FTP (управление)",
                22: "SSH (безопасное удаленное управление)",
                23: "Telnet (удаленное управление)",
                25: "SMTP (почтовая служба)",
                53: "DNS (система имен доменов)",
                80: "HTTP (веб-сервер)",
                110: "POP3 (получение почты)",
                143: "IMAP (получение почты)",
                443: "HTTPS (защищенный веб-сервер)",
                465: "SMTPS (защищенная почтовая служба)",
                993: "IMAPS (защищенный IMAP)",
                995: "POP3S (защищенный POP3)",
                3389: "RDP (удаленный рабочий стол)",
                8000: "IP камера",
                8080: "IP камера",
                83: "IP камера",
                60001: "IP камера"
            }

            # Добавляем стандартные порты Minecraft
            for port in range(25000, 27001):
                standard_ports[port] = "Minecraft (стандартный порт)"

            # Сканирование стандартных портов и портов из словаря
            open_ports = []
            for port in range(start_port, end_port + 1):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((target_ip, port))
                    if result == 0:
                        service_name = get_service_name(port, standard_ports)
                        print(f"Активный порт: {port}, Служба: {service_name}")
                        open_ports.append(port)

        else:
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

# Функция для ввода начального и конечного порта
def input_ports():
    start_port = int(input("Введите начальный порт (используйте -1 для сканирования стандартных портов, Minecraft, IP камер): "))

    # Если начальный порт -1, то не запрашиваем конечный порт
    if start_port == -1:
        return start_port, start_port

    end_port = int(input("Введите конечный порт: "))
    return start_port, end_port

# Функция для получения имени службы по порту
def get_service_name(port, standard_ports=None):
    try:
        import socket
        if standard_ports and port in standard_ports:
            return standard_ports[port]
        else:
            return socket.getservbyport(port)  # Возвращает имя службы, если порт не стандартный
    except (socket.error, OSError):
        return "Неизвестно"

# Функция для записи результатов сканирования в лог-файл
def log_scan_results(target_ip, open_ports):
    log_folder = "logs"
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    now = datetime.datetime.now()
    log_filename = os.path.join(log_folder, now.strftime("%Y-%m-%d_%H-%M-%S_scan.log"))

    logging.basicConfig(filename=log_filename, level=logging.INFO)
    logging.info(f"Сканирование портов для IP-адреса {target_ip} завершено.")
    for port in open_ports:
        service_name = get_service_name(port)
        logging.info(f"Активный порт: {port}, Служба: {service_name}")

# Функция для проверки обновлений
def check_for_updates():
    try:
        clear_console()  # Очистка консоли перед проверкой обновления
        print("Проверка обновлений...")

        # Загрузка версии и изменений из файла Update.txt на GitHub
        update_url = "https://raw.githubusercontent.com/KailJ1/PortScan/main/Update.txt"
        response = requests.get(update_url)

        if response.status_code == 200:
            remote_data = response.content.decode("utf-8").strip().split("\n")
            remote_version = remote_data[0].split(": ")[1].strip()

            with open("Update.txt", "r", encoding="utf-8") as local_file:
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

# Функция для скачивания и применения обновления
def download_update():
    try:
        update_url = "https://github.com/KailJ1/PortScan/archive/main.zip"
        response = requests.get(update_url)
        if response.status_code == 200:
            clear_console()  # Очистка консоли перед установкой обновления
            print("Обновление устанавливается...")

            with open("update.zip", "wb") as zip_file:
                zip_file.write(response.content)

            # Распаковать архив
            with zipfile.ZipFile("update.zip", "r") as zip_ref:
                zip_ref.extractall("PortScan-main")

            # Заменить файлы
            for root, dirs, files in os.walk("PortScan-main"):
                for file in files:
                    src_path = os.path.join(root, file)
                    dest_path = os.path.join(".", file)
                    shutil.copy2(src_path, dest_path)

            # Удалить временную папку и архив
            shutil.rmtree("PortScan-main")
            os.remove("update.zip")

            print("Обновление успешно установлено. Пожалуйста, перезапустите программу для применения обновления.")
            
            input("Нажмите Enter для перезапуска программы...")
            
            # Перезапустить программу
            subprocess.call(["python", "Port-Scanner.py"])
            exit()  # Завершить текущий экземпляр программы

        else:
            print("Не удалось скачать обновление.")
    except Exception as e:
        print(f"Ошибка при скачивании и установке обновления: {str(e)}")

# Главный блок программы
if __name__ == "__main__":
    processed_ports = 0

    clear_console()

    print("Программа сканирования портов")
    
    # Проверка обновлений
    check_for_updates()
    
    target_ip = input("Введите IP-адрес для сканирования: ")
    
    start_port, end_port = input_ports()
    
    print("Идет сканирование...")
    scan_ports(target_ip, start_port, end_port)

    # Здесь добавляем предложение ввести 0 для продолжения после завершения сканирования
    input("Сканирование завершено. Введите 0 для продолжения: ")
