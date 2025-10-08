# cbhands - Battle Hands Service Manager

**Version:** 0.2.0  
**Author:** Battle Hands Team  
**Description:** Утилита для управления сервисами игры Battle Hands с поддержкой плагинов

## 🚀 Возможности

- **Управление сервисами**: Запуск, остановка, перезапуск сервисов Battle Hands
- **Система плагинов**: Расширяемая архитектура с поддержкой плагинов
- **Мониторинг**: Отслеживание состояния сервисов и логи
- **Конфигурация**: Гибкая настройка через YAML файлы
- **Цветной вывод**: Удобный интерфейс с цветным форматированием
- **SSL поддержка**: Работа с HTTPS сервисами
- **Домен интеграция**: Поддержка доменов с nginx reverse proxy

## 📊 Текущий статус системы

**Версия:** 0.2.0  
**Статус:** ✅ Активная разработка  
**Последнее обновление:** 2025-10-08  

### Доступные сервисы
- **lobby_py** - Lobby Service (Python) - Управление столами
- **dealer** - Dealer Service (Go) - Игровая логика
- **battle_hands_ts** - Frontend (TypeScript) - Пользовательский интерфейс
- **cbhands_monitor_ts** - Monitor Service (TypeScript) - Мониторинг

### Активные плагины
- **dev-showroom (v0.2.0)** - Полностью функциональный
- **use-games (v0.2.0)** - Базовый функционал

### Инфраструктура
- **Домен:** https://test.battlehands.online (SSL настроен)
- **Nginx:** Reverse proxy с SSL поддержкой
- **Redis:** Кэширование и pub/sub
- **SSL:** Let's Encrypt сертификаты (до 2026-01-06)

## 📦 Установка

### Через pipx (рекомендуется)
```bash
pipx install -e .
```

### Через pip
```bash
pip install -e .
```

## 🎯 Основные команды

### Управление сервисами
```bash
# Запуск сервиса
cbhands start <service_name>

# Остановка сервиса
cbhands stop <service_name>

# Перезапуск сервиса
cbhands restart <service_name>

# Статус сервисов (с отображением портов)
cbhands status [service_name]

# Список доступных сервисов
cbhands list-services
```

### Мониторинг
```bash
# Просмотр логов
cbhands logs <service_name> [--lines N] [--follow]

# Мониторинг в реальном времени
cbhands monitor watch
```

### Статус сервисов
Команда `cbhands status` отображает подробную информацию о всех сервисах:
- **Порт**: Порт сервиса (отображается для всех сервисов)
- **PID**: Идентификатор процесса (для запущенных сервисов)
- **Uptime**: Время работы (для запущенных сервисов)
- **Статус**: Состояние сервиса (running/stopped)

**Пример вывода:**
```
Battle Hands Services Status
==================================================
● lobby
    Lobby Service - Table management and WebSocket connections
    Port: 6001
    PID: 596273
    Uptime: 00:29:37

○ frontend
    Frontend - Battle Hands TypeScript application
    Port: 3000
    Status: stopped
```

### Плагины
```bash
# Список доступных плагинов
cbhands plugins

# Помощь по плагину
cbhands dev-showroom --help
cbhands use-games --help

# Работа с dev-showroom
cbhands dev-showroom create-tables --count 5 --mode fun
cbhands dev-showroom list-tables
cbhands dev-showroom show-redis

# Работа с use-games
cbhands use-games test --test "5-3-test"
```

## 🔌 Система плагинов

cbhands поддерживает расширяемую архитектуру плагинов. Каждый плагин может добавлять свои команды в CLI.

### Доступные плагины

#### dev-showroom (v0.2.0)
**Репозиторий:** [cbhands_dev_showroom](https://github.com/battle-hands/cbhands_dev_showroom)  
**Описание:** Development Showroom - Interactive testing and demonstration tool  
**Статус:** ✅ Активный, полностью функциональный

**Команды:**
```bash
# Создание таблиц
cbhands dev-showroom create-tables --count 10 --mode fun

# Просмотр таблиц
cbhands dev-showroom list-tables

# Детали таблицы
cbhands dev-showroom show-table --name "table-1"

# Удаление таблиц
cbhands dev-showroom delete-tables --all
cbhands dev-showroom delete-tables --name "table-1"

# Просмотр Redis данных
cbhands dev-showroom show-redis

# Интерактивный режим
cbhands dev-showroom interactive
```

**Возможности:**
- Создание тестовых игровых столов
- Управление Redis данными
- Интерактивное тестирование функциональности
- Интеграция с Lobby API
- Поддержка различных игровых режимов

#### use-games (v0.2.0)
**Репозиторий:** [cbhands_use_games](https://github.com/battle-hands/cbhands_use_games)  
**Описание:** Game Testing - Testing utilities for Battle Hands  
**Статус:** ✅ Активный, базовый функционал

**Команды:**
```bash
# Тестирование игр
cbhands use-games test --test "5-3-test"
```

**Возможности:**
- Утилиты для тестирования игровой логики
- Интеграция с игровыми сервисами
- Автоматизированное тестирование сценариев

### Разработка плагинов

#### Структура плагина
```
my_plugin/
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── cli.py
├── setup.py
└── README.md
```

#### Пример плагина

**my_plugin/__init__.py:**
```python
"""My Plugin package."""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "My custom plugin for cbhands"
```

**my_plugin/plugin.py:**
```python
"""Main plugin for my_plugin."""

import click
from typing import Dict
from colorama import Fore, Style

class MyPlugin:
    """cbhands plugin for my functionality."""
    
    def __init__(self):
        """Initialize the plugin."""
        self.name = "my_plugin"
        self.description = "My custom plugin for cbhands"
    
    def get_commands(self) -> Dict[str, callable]:
        """Get plugin commands.
        
        Returns:
            Dictionary of command name -> callable
        """
        return {
            "my-command": self.my_command,
            "another-command": self.another_command,
        }
    
    def my_command(self, verbose=False, config=None):
        """My custom command."""
        try:
            click.echo(f"{Fore.CYAN}My Custom Command{Style.RESET_ALL}")
            click.echo("=" * 30)
            
            if verbose:
                click.echo("Verbose mode enabled")
            
            click.echo(f"{Fore.GREEN}✅ Command executed successfully{Style.RESET_ALL}")
                
        except Exception as e:
            click.echo(f"\n{Fore.RED}❌ Failed: {e}{Style.RESET_ALL}", err=True)
            return
    
    def another_command(self, verbose=False, config=None):
        """Another custom command."""
        click.echo(f"{Fore.YELLOW}Another command executed{Style.RESET_ALL}")
```

**setup.py:**
```python
#!/usr/bin/env python3
"""Setup script for my_plugin."""

from setuptools import setup, find_packages

setup(
    name="my_plugin",
    version="0.1.0",
    author="Your Name",
    description="My custom plugin for cbhands",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "cbhands.plugins": [
            "my_plugin=my_plugin.plugin:MyPlugin",
        ],
    },
)
```

#### Установка плагина
```bash
# Установка в pipx среде cbhands
/home/jk/.local/share/pipx/venvs/cbhands/bin/python -m pip install -e /path/to/my_plugin

# Или через pip
pip install -e /path/to/my_plugin
```

## ⚙️ Конфигурация

### Файл конфигурации
```yaml
# config/default.yaml
services:
  lobby:
    description: "Lobby Service - WebSocket server for table management"
    port: 12120
    command: "cd /path/to/lobby && ./lobby"
    working_dir: "/path/to/lobby"
    
  dealer:
    description: "Dealer Service - Game logic server"
    port: 8080
    command: "cd /path/to/dealer && ./dealer"
    working_dir: "/path/to/dealer"
    
  cbhands_monitor_ts:
    description: "Monitor Service - Real-time monitoring"
    port: 9000
    command: "cd /path/to/monitor && npm start"
    working_dir: "/path/to/monitor"
```

### Использование конфигурации
```bash
# Использование конкретного файла конфигурации
cbhands -c /path/to/config.yaml start lobby

# Просмотр статуса с конфигурацией
cbhands -c /path/to/config.yaml status

# Работа с плагинами с конфигурацией
cbhands -c /home/jk/battles/cbhands/config/default.yaml dev-showroom --help
cbhands -c /home/jk/battles/cbhands/config/default.yaml dev-showroom create-tables --count 5
```

**Примечание:** Если конфигурационный файл не указан, cbhands будет искать его в текущей директории. Рекомендуется всегда указывать путь к конфигурации явно.

## 🛠️ Разработка

### Установка для разработки
```bash
git clone <repository>
cd cbhands
pip install -e .
```

### Запуск тестов
```bash
python -m pytest tests/
```

### Структура проекта
```
cbhands/
├── cbhands/
│   ├── __init__.py
│   ├── cli.py          # Основной CLI интерфейс
│   ├── config.py       # Управление конфигурацией
│   ├── manager.py      # Управление сервисами
│   └── logger.py       # Логирование
├── config/
│   ├── default.yaml    # Конфигурация по умолчанию
│   └── test_config.yaml
├── tests/
│   ├── test_config.py
│   └── test_manager.py
├── setup.py
└── README.md
```

## 📝 Логирование

cbhands использует структурированное логирование:
- Логи сервисов сохраняются в `~/.local/share/cbhands/logs/`
- Ротация логов по размеру и времени
- Цветной вывод в консоли

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Создайте Pull Request

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

## 🆘 Поддержка

Если у вас есть вопросы или проблемы:
1. Проверьте [Issues](https://github.com/battle-hands/cbhands/issues)
2. Создайте новый Issue с подробным описанием
3. Свяжитесь с командой разработки

## 🔗 Связанные проекты

### Основные компоненты
- [battle_hands](https://github.com/battle-hands/battle_hands) - Основной проект Battle Hands (документация и планирование)
- [battle_hands_ts](https://github.com/battle-hands/battle_hands_ts) - TypeScript фронтенд приложение
- [lobby](https://github.com/battle-hands/lobby) - Сервис управления столами (Go)
- [dealer](https://github.com/battle-hands/dealer) - Сервис обработки игр (Go)

### Плагины cbhands
- [cbhands_dev_showroom](https://github.com/battle-hands/cbhands_dev_showroom) - Плагин для демонстрации и тестирования (v0.2.0)
- [cbhands_use_games](https://github.com/battle-hands/cbhands_use_games) - Плагин для тестирования игр (v0.2.0)

### Инфраструктура и мониторинг
- [cbhands_monitor_ts](https://github.com/battle-hands/cbhands_monitor_ts) - Мониторинг сервисов (TypeScript)

### Методология и аналитика
- [battles_keep_kaip](https://github.com/battle-hands/battles_keep_kaip) - Keep KAIP методология для AI-разработки
- [Keep_AI_Prompts](https://github.com/battle-hands/Keep_AI_Prompts) - AI промпты и методология

---

**Battle Hands Team** - Создано с ❤️ для разработчиков