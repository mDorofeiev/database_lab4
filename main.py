import sys
from datetime import datetime
from src.database import SessionLocal, PG_URL, MYSQL_URL
from src.services import WeatherService

def print_menu():
    print('\n1. Імпортувати дані з GlobalWeatherRepository.csv')
    print('2. Пошук погоди за країною та датою')
    print('3. Реплікувати дані: PostgreSQL -> MySQL')
    print('4. Реплікувати дані: MySQL -> PostgreSQL')
    print('0. Вихід')

def handle_search(service):
    country = input('Введіть країну (наприклад, Ukraine, Poland): ').strip()
    date_str = input('Введіть дату у форматі YYYY-MM-DD (наприклад, 2024-05-16): ').strip()
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print('Невірний формат дати. Використовуйте YYYY-MM-DD.')
        return

    location = input('Місто/локація (необов\'язково, Enter щоб пропустити): ').strip() or None
    safe_filter_str = input(
        'Фільтр "Чи варто виходити на вулицю?" (y - так, n - ні, Enter - всі): '
    ).strip().lower()

    only_safe = None
    if safe_filter_str == 'y':
        only_safe = True
    elif safe_filter_str == 'n':
        only_safe = False

    results = service.search_weather(
        country=country,
        target_date=target_date,
        location_name=location,
        only_safe_outside=only_safe
    )

    if not results:
        print('\nЗа вашим запитом записів не знайдено.')
        return

    print(f'\nЗнайдено записів: {len(results)}')
    print('-' * 95)
    for r in results:
        w = r.wind_info
        go_out_text = 'Так' if w.should_go_outside else 'Ні'
        print(
            f'[{r.last_updated}] {r.country}, {r.location_name} | '
            f'Темп: {r.temperature_celsius}°C | Схід сонця: {r.sunrise}\n'
            f'   -> Вітер: {w.wind_kph} км/год ({w.wind_mph} миль/год), '
            f'Напрямок: {w.wind_direction.value} ({w.wind_degree}°), '
            f'Пориви: {w.gust_kph} км/год | Виходити на вулицю: {go_out_text}'
        )
    print('-' * 95)

def main():
    session = SessionLocal()
    service = WeatherService(session)

    while True:
        print_menu()
        choice = input('Оберіть дію: ').strip()

        if choice == '1':
            csv_path = input('Шлях до CSV [GlobalWeatherRepository.csv]: ').strip() or 'GlobalWeatherRepository.csv'
            limit_str = input('Ліміт рядків (Enter для завантаження всіх): ').strip()
            limit = int(limit_str) if limit_str.isdigit() else None
            count = service.import_from_csv(csv_path, limit=limit)
            print(f'Імпортовано {count} записів.')
        elif choice == '2':
            handle_search(service)
        elif choice == '3':
            count = service.replicate_database(PG_URL, MYSQL_URL)
            print(f'Перенесено {count} записів із PostgreSQL у MySQL.')
        elif choice == '4':
            count = service.replicate_database(MYSQL_URL, PG_URL)
            print(f'Перенесено {count} записів із MySQL у PostgreSQL.')
        elif choice == '0':
            session.close()
            sys.exit(0)
        else:
            print('Невідома команда, спробуйте ще раз.')

if __name__ == '__main__':
    main()