import csv
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models import WeatherReport, WindInfo, WindDirection
from src.repositories import WeatherRepository
from src.database import get_session_for_url

class WeatherService:
    def __init__(self, session):
        self.repo = WeatherRepository(session)

    @staticmethod
    def evaluate_should_go_outside(wind_kph, gust_kph, temp_c = None):
        wind_safe = (wind_kph <= 36.0) and (gust_kph <= 50.0)
        if temp_c is not None:
            temp_safe = -15.0 <= temp_c <= 38.0
            return wind_safe and temp_safe
        return wind_safe

    def import_from_csv(self, csv_path, limit = None):
        reports_to_insert: List[WeatherReport] = []
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if limit and idx >= limit:
                    break

                # Парсинг дати
                dt_str = row['last_updated'].strip()
                parsed_date = datetime.strptime(dt_str.split()[0], '%Y-%m-%d').date()

                # Парсинг часу сходу сонця
                sunrise_str = row['sunrise'].strip()
                parsed_sunrise = datetime.strptime(sunrise_str, '%I:%M %p').time()

                wind_kph = float(row['wind_kph'])
                gust_kph = float(row['gust_kph'])
                temp_c = float(row['temperature_celsius'])
                direction_str = row['wind_direction'].strip().upper()

                report = WeatherReport(
                    country=row['country'].strip(),
                    location_name=row['location_name'].strip(),
                    temperature_celsius=temp_c,
                    last_updated=parsed_date,
                    sunrise=parsed_sunrise,
                    wind_info=WindInfo(
                        wind_mph=float(row['wind_mph']),
                        wind_kph=wind_kph,
                        wind_degree=int(row['wind_degree']),
                        wind_direction=WindDirection(direction_str),
                        gust_mph=float(row['gust_mph']),
                        gust_kph=gust_kph,
                        should_go_outside=self.evaluate_should_go_outside(
                            wind_kph=wind_kph,
                            gust_kph=gust_kph,
                            temp_c=temp_c
                        )
                    )
                )
                reports_to_insert.append(report)

        self.repo.add_reports_bulk(reports_to_insert)
        return len(reports_to_insert)

    def search_weather(self, country, target_date, location_name = None, only_safe_outside = None):
        return self.repo.find_weather(
            country=country,
            target_date=target_date,
            location_name=location_name,
            only_safe_outside=only_safe_outside
        )

    @staticmethod
    def replicate_database(source_url, target_url):
        src_session, _ = get_session_for_url(source_url)
        tgt_session, _ = get_session_for_url(target_url)

        try:
            src_repo = WeatherRepository(src_session)
            tgt_repo = WeatherRepository(tgt_session)

            tgt_session.query(WindInfo).delete()
            tgt_session.query(WeatherReport).delete()
            tgt_session.commit()

            all_records = src_repo.get_all_reports()
            cloned_records: List[WeatherReport] = []

            for rec in all_records:
                new_report = WeatherReport(
                    id=rec.id,
                    country=rec.country,
                    location_name=rec.location_name,
                    temperature_celsius=rec.temperature_celsius,
                    last_updated=rec.last_updated,
                    sunrise=rec.sunrise,
                    wind_info=WindInfo(
                        id=rec.wind_info.id,
                        wind_mph=rec.wind_info.wind_mph,
                        wind_kph=rec.wind_info.wind_kph,
                        wind_degree=rec.wind_info.wind_degree,
                        wind_direction=rec.wind_info.wind_direction,
                        gust_mph=rec.wind_info.gust_mph,
                        gust_kph=rec.wind_info.gust_kph,
                        should_go_outside=rec.wind_info.should_go_outside
                    )
                )
                cloned_records.append(new_report)

            tgt_repo.add_reports_bulk(cloned_records)
            return len(cloned_records)
        finally:
            src_session.close()
            tgt_session.close()