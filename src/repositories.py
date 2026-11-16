from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from src.models import WeatherReport, WindInfo

class WeatherRepository:
    def __init__(self, session):
        self.session = session

    def add_reports_bulk(self, reports):
        self.session.add_all(reports)
        self.session.commit()

    def get_all_reports(self):
        return (
            self.session.query(WeatherReport)
            .options(joinedload(WeatherReport.wind_info))
            .all()
        )

    def find_weather(self, country, target_date, location_name = None, only_safe_outside = None):
        query = (
            self.session.query(WeatherReport)
            .join(WeatherReport.wind_info)
            .options(joinedload(WeatherReport.wind_info))
            .filter(
                WeatherReport.country.ilike(f'%{country.strip()}%'),
                WeatherReport.last_updated == target_date
            )
        )
        if location_name:
            query = query.filter(WeatherReport.location_name.ilike(f'%{location_name.strip()}%'))
        if only_safe_outside is not None:
            query = query.filter(WindInfo.should_go_outside == only_safe_outside)

        return query.all()