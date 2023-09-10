#!/bin/bash

# Установка кодировки UTF-8
export LANG=en_US.UTF-8

# Проверяем наличие библиотеки 'requests'
python3 -c "import requests" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Установка библиотеки 'requests'..."
    pip3 install requests

    if [ $? -ne 0 ]; then
        echo "Не удалось установить библиотеку 'requests'. Пожалуйста, установите ее вручную и затем запустите программу."
    else
        echo "Библиотека 'requests' успешно установлена."
        read -p "Нажмите Enter для продолжения..."
        python3 Port-Scanner.py
    fi
else
    echo "Библиотека 'requests' уже установлена."
    read -p "Нажмите Enter для продолжения..."
    python3 Port-Scanner.py
fi
