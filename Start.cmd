@echo off
chcp 1251 > nul
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Установка библиотеки 'requests'...
    pip install requests
    if errorlevel 1 (
        echo Не удалось установить библиотеку 'requests'. Пожалуйста, установите ее вручную и затем запустите программу.
    ) else (
        echo Библиотека 'requests' успешно установлена.
        pause
        python Port-Scanner.py
    )
) else (
    echo Библиотека 'requests' уже установлена.
    pause
    python Port-Scanner.py
)
