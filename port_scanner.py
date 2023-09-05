import socket
import datetime
import logging
import os
import threading
import concurrent.futures
import sys

# Глобальная переменная для хранения количества обработанных портов
processed_ports = 0

# Функция для сканирования портов в указанном диапазоне на заданном IP
def scan_ports(target_ip, start_port, end_port):
    open_ports = []
    total_ports = end_port - start_port + 1

    def scan_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((target_ip, port))
            open_ports.append(port)
        except (socket.timeout, ConnectionRefusedError):
            pass
        finally:
            global processed_ports
            processed_ports += 1
            progress = processed_ports / total_ports * 100
            sys.stdout.write(f"\rПрогресс: {progress:.2f}%")
            sys.stdout.flush()

    if start_port == -1:
        # Если указан порт -1, сканируем только стандартные порты и диапазон от 25560 до 25580
        standard_ports = [21, 22, 80, 443, 3306, 8000, 8080]
        additional_ports = list(range(25560, 25581))
        total_ports += len(standard_ports) + len(additional_ports)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for port in standard_ports + additional_ports:
                executor.submit(scan_port, port)
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for port in range(start_port, end_port + 1):
                executor.submit(scan_port, port)

    sys.stdout.write("\n")  # Переводим строку после завершения сканирования
    sys.stdout.flush()

    return open_ports

# Функция для записи логов в файл
def log_scan_results(target_ip, open_ports):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_directory = "logs"
    log_filename = f"{log_directory}/{current_datetime}_scan.log"

    # Проверяем наличие директории "logs" и создаем ее, если она отсутствует
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logging.basicConfig(filename=log_filename, level=logging.INFO)
    logging.info(f"Сканирование портов на {target_ip}")

    for port in open_ports:
        service_name = get_service_name(port)
        logging.info(f"IP: {target_ip}, Port: {port}, Service: {service_name}")

# Функция для определения службы, прослушивающей на порту
def get_service_name(port):
    # Добавляем описание "IP камера" для портов 8000 и 8080
    if port in [8000, 8080]:
        return "IP камера"
    
    # Добавляем сервис для портов от 25560 до 25580
    if 25560 <= port <= 25580:
        return "Minecraft Server"

    # Добавьте здесь соответствия портов и служб, если необходимо
    services = {
        21: "FTP",
        22: "SSH",
        80: "HTTP",
        443: "HTTPS",
        3306: "MySQL",
    }
    
    return services.get(port, "Неизвестно")

if __name__ == "__main__":
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
    else:
        print("На заданном IP нет активных портов.")
