# Визуальный редактор диаграмм

Десктопное приложение для создания, редактирования и визуализации диаграмм с сохранением данных в PostgreSQL.

## Технологии

- **PyQt6** — графический интерфейс
- **SQLAlchemy** — работа с базой данных
- **PostgreSQL** — хранение данных
- **Matplotlib** — отрисовка диаграмм
- **Pandas + openpyxl** — экспорт данных

## Возможности

- Создание диаграмм трёх типов: **bar**, **line**, **pie**
- Редактирование данных в реальном времени (график обновляется сразу)
- Сохранение и загрузка диаграмм из БД
- Одновременная работа с несколькими диаграммами
- Экспорт данных в Excel (2 листа: информация о диаграмме + данные)
- Сохранение диаграммы как изображение (PNG, SVG)
- Фильтрация списка диаграмм по типу

## Структура проекта

```
diagram_editor/
├── main.py                    # Точка входа
├── config.py                  # Настройки подключения к БД
├── database.py                # Подключение к БД и CRUD-операции
├── models.py                  # Модели SQLAlchemy (Diagram, DiagramData)
├── ui/
│   ├── main_window.py         # Главное окно
│   ├── edit_window.py         # Окно редактирования данных
│   └── plot_window.py         # Окно отображения графика
├── controllers/
│   └── diagram_controller.py  # Логика работы с диаграммами
├── resources/                 # Ресурсы (иконки и т.д.)
├── requirements.txt           # Зависимости
└── README.md
```

## Установка

### 1. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Настроить подключение к БД

В файле `config.py` указать свои данные:

```python
DATABASE_CONFIG = {
    "drivername": "postgresql",
    "username": "postgres",
    "password": "ваш_пароль",
    "host": "localhost",
    "port": "5432",
    "database": "diagram_editor_db"
}
```

### 3. Создать базу данных

```sql
CREATE DATABASE diagram_editor_db;
```

Таблицы `diagrams` и `diagram_data` создаются автоматически при первом запуске.

## Запуск

```bash
python main.py
```

## Схема БД

**`diagrams`** — основная информация о диаграмме:

| Поле         | Тип      | Описание             |
|--------------|----------|----------------------|
| id           | Integer  | Первичный ключ       |
| name         | String   | Название диаграммы   |
| diagram_type | String   | Тип (bar/line/pie)   |
| title        | String   | Заголовок графика    |
| xlabel       | String   | Подпись оси X        |
| ylabel       | String   | Подпись оси Y        |
| created_at   | DateTime | Дата создания        |

**`diagram_data`** — данные диаграммы:

| Поле       | Тип     | Описание                    |
|------------|---------|-----------------------------|
| id         | Integer | Первичный ключ              |
| diagram_id | Integer | Внешний ключ → diagrams.id  |
| label      | String  | Метка                       |
| value      | Float   | Значение                    |
| position   | Integer | Порядок отображения         |