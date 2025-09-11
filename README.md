# cbhands

Battle Hands Service Manager - утилита для управления сервисами игры Battle Hands.

## Описание

`cbhands` - это утилита командной строки для управления сервисами Battle Hands, аналогичная `systemctl`. Позволяет запускать, останавливать, перезапускать сервисы и получать их логи.

## Установка

```bash
pip install -e .
```

## Использование

### Основные команды

```bash
# Запуск сервиса
cbhands start dealer

# Остановка сервиса
cbhands stop dealer

# Перезапуск сервиса
cbhands restart dealer

# Статус сервиса
cbhands status dealer

# Статус всех сервисов
cbhands status

# Логи сервиса
cbhands logs dealer

# Следить за логами
cbhands logs -f dealer
```

### Конфигурация

Конфигурация сервисов хранится в `config/default.yaml`:

```yaml
services:
  dealer:
    port: 6000
    command: "cd /home/jk/btl_dev_fullai/dealer && ./bin/dealer"
    working_directory: "/home/jk/btl_dev_fullai/dealer"
    health_endpoint: "/v1/dealer/health"
    
  lobby_py:
    port: 6001
    command: "cd /home/jk/btl_dev_fullai/lobby_py && source venv/bin/activate && python3 main.py --debug"
    working_directory: "/home/jk/btl_dev_fullai/lobby_py"
    health_endpoint: "/api/v1/health"
    
  battle_hands_ts:
    port: 8080
    command: "cd /home/jk/btl_dev_fullai/battle_hands_ts && npm run dev"
    working_directory: "/home/jk/btl_dev_fullai/battle_hands_ts"
    health_endpoint: "/"
```

## Разработка

```bash
# Установка в режиме разработки
pip install -e .

# Запуск тестов
python -m pytest tests/

# Линтинг
flake8 cbhands/
```

## Лицензия

MIT