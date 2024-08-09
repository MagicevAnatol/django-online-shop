## Установка и настройка проекта

Следуйте этим инструкциям, чтобы настроить и запустить проект на вашей локальной машине.

### 1. Клонирование репозитория

Клонируйте репозиторий на вашу локальную машину

### 2. Создание виртуального окружения:

Создайте виртуальное окружение для изолированной установки зависимостей, если у вас его нет:

```sh 
python -m venv venv
source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
```

### 3. Установка зависимостей

Установите необходимые пакеты, используя pip:

```sh 
pip install -r requirements.txt
```

### 4. Установка пакета фронт-энда

Для установки пакета перейди в директорию diploma-frontend, далее используйте команды:

```sh
cd diploma-frontend/
python setup.py sdist
pip install dist/diploma-frontend-0.6.tar.gz 
```

### 5. Запуск БД

Запустите базу данных, в проекте используется PostgreSQL, для запуска контейнера воспользуйтесь созданным docker compose.
Флаг -d предназначен для запуска в фоновом режиме.
```sh 
docker-compose up -d
```


### 6. Применение миграций

Примените миграции для настройки базы данных, для начала запустите сервер для создания базы
данных, остановите, накатите миграции:

```sh 
cd shop/
python manage.py migrate
```

### 7. Загрузка данных

Для загрузки предустановленных данных используйте команду:

```sh 
python import_data.py
```

### 8. Запуск сервера разработки

Запустите сервер разработки:

```sh 
python manage.py runserver
```

### 9. Дополнительные настройки

Сброс базы данных
Если вам нужно сбросить базу данных и начать заново:

```sh 
python manage.py flush
python manage.py migrate
python manage.py loaddata data.json
```

Если необходимо использовать redis (для кэширования) использовать файл docker-compose.yml.
Раскомментируйте CACHES в settings.py и создание контейнера в docker compose.

```sh 
docker-compose up --build
```

Если необходимо изменить JS или другие данные фронт-энда, установить пакет с флагом --no-cache-dir, 
чтобы избежать проблем с кэшированием пакетов:
```sh
pip install --no-cache-dir dist/diploma-frontend-0.6.tar.gz
```