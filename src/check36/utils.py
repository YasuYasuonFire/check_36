"""Utility functions for date and time calculations"""

import calendar
from datetime import datetime


def get_days_in_month(year: int, month: int) -> int:
    """月の日数を取得"""
    return calendar.monthrange(year, month)[1]


def parse_date(date_str: str) -> tuple[int, int, int]:
    """日付文字列をパース (year, month, day)"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.year, dt.month, dt.day


def get_current_date() -> str:
    """現在の日付を取得 (YYYY-MM-DD)"""
    return datetime.now().strftime("%Y-%m-%d")


def calculate_legal_work_hours(days_in_month: int) -> float:
    """月の法定労働時間を計算
    
    計算式: (月の暦日数 ÷ 7) × 40時間
    """
    return (days_in_month / 7) * 40

