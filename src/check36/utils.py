"""Utility functions for date and time calculations"""

import calendar
from datetime import datetime, timedelta


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


def count_weekdays(start_date: str, end_date: str) -> int:
    """指定期間内の平日（月〜金）の日数をカウント
    
    Args:
        start_date: 開始日（YYYY-MM-DD形式、この日を含む）
        end_date: 終了日（YYYY-MM-DD形式、この日を含む）
    
    Returns:
        平日の日数（土日を除く）
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    if start > end:
        return 0
    
    weekday_count = 0
    current = start
    
    while current <= end:
        # 月曜日=0, 日曜日=6
        if current.weekday() < 5:  # 月〜金（0-4）
            weekday_count += 1
        current += timedelta(days=1)
    
    return weekday_count


def get_remaining_weekdays_in_month(current_date: str) -> int:
    """当月の残り平日数を取得（今日を含む）
    
    Args:
        current_date: 基準日（YYYY-MM-DD形式）
    
    Returns:
        今日を含む当月末までの平日数
    """
    year, month, day = parse_date(current_date)
    days_in_month = get_days_in_month(year, month)
    
    # 月末日を取得
    end_of_month = f"{year:04d}-{month:02d}-{days_in_month:02d}"
    
    return count_weekdays(current_date, end_of_month)


def get_elapsed_weekdays_in_month(current_date: str) -> int:
    """当月の経過平日数を取得（昨日まで）
    
    Args:
        current_date: 基準日（YYYY-MM-DD形式）
    
    Returns:
        月初から昨日までの平日数
    """
    year, month, day = parse_date(current_date)
    
    if day == 1:
        # 月初の場合は0
        return 0
    
    # 月初日を取得
    start_of_month = f"{year:04d}-{month:02d}-01"
    
    # 昨日の日付を取得
    current = datetime.strptime(current_date, "%Y-%m-%d")
    yesterday = current - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    return count_weekdays(start_of_month, yesterday_str)

