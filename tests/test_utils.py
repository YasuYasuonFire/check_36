"""Tests for utility functions"""

import pytest
from datetime import datetime

from check36.utils import (
    count_weekdays,
    get_elapsed_weekdays_in_month,
    get_remaining_weekdays_in_month,
)


class TestCountWeekdays:
    """count_weekdays関数のテスト"""

    def test_count_weekdays_single_week(self):
        """1週間の平日カウント"""
        # 2025-10-20 (月) から 2025-10-24 (金) まで
        result = count_weekdays("2025-10-20", "2025-10-24")
        assert result == 5

    def test_count_weekdays_with_weekend(self):
        """週末を含む期間の平日カウント"""
        # 2025-10-20 (月) から 2025-10-26 (日) まで
        result = count_weekdays("2025-10-20", "2025-10-26")
        assert result == 5  # 月〜金のみ

    def test_count_weekdays_saturday_to_saturday(self):
        """土曜日から土曜日まで"""
        # 2025-10-25 (土) から 2025-11-01 (土) まで
        result = count_weekdays("2025-10-25", "2025-11-01")
        assert result == 5  # 月〜金のみ

    def test_count_weekdays_single_day_weekday(self):
        """1日のみ（平日）"""
        # 2025-10-20 (月)
        result = count_weekdays("2025-10-20", "2025-10-20")
        assert result == 1

    def test_count_weekdays_single_day_weekend(self):
        """1日のみ（週末）"""
        # 2025-10-25 (土)
        result = count_weekdays("2025-10-25", "2025-10-25")
        assert result == 0

    def test_count_weekdays_full_month(self):
        """1ヶ月全体"""
        # 2025年10月 (31日)
        result = count_weekdays("2025-10-01", "2025-10-31")
        # 10月は水曜日始まり、金曜日終わり
        # 平日: 23日
        assert result == 23

    def test_count_weekdays_invalid_range(self):
        """無効な範囲（終了日が開始日より前）"""
        result = count_weekdays("2025-10-25", "2025-10-20")
        assert result == 0


class TestGetRemainingWeekdaysInMonth:
    """get_remaining_weekdays_in_month関数のテスト"""

    def test_remaining_weekdays_from_monday(self):
        """月曜日からの残り平日"""
        # 2025-10-20 (月) から月末まで
        result = get_remaining_weekdays_in_month("2025-10-20")
        # 10/20-10/24 (5日) + 10/27-10/31 (5日) = 10日
        assert result == 10

    def test_remaining_weekdays_from_saturday(self):
        """土曜日からの残り平日"""
        # 2025-10-25 (土) から月末まで
        result = get_remaining_weekdays_in_month("2025-10-25")
        # 10/27-10/31 (5日)
        assert result == 5

    def test_remaining_weekdays_from_first_day(self):
        """月初からの残り平日"""
        # 2025-10-01 (水) から月末まで
        result = get_remaining_weekdays_in_month("2025-10-01")
        # 10月全体の平日数
        assert result == 23

    def test_remaining_weekdays_from_last_day(self):
        """月末日の残り平日"""
        # 2025-10-31 (金)
        result = get_remaining_weekdays_in_month("2025-10-31")
        assert result == 1  # 今日のみ


class TestGetElapsedWeekdaysInMonth:
    """get_elapsed_weekdays_in_month関数のテスト"""

    def test_elapsed_weekdays_from_monday(self):
        """月曜日時点での経過平日（昨日まで）"""
        # 2025-10-20 (月) の時点で、昨日までの平日
        result = get_elapsed_weekdays_in_month("2025-10-20")
        # 10/01-10/17 (金) まで = 13日
        assert result == 13

    def test_elapsed_weekdays_from_saturday(self):
        """土曜日時点での経過平日（昨日まで）"""
        # 2025-10-25 (土) の時点で、昨日までの平日
        result = get_elapsed_weekdays_in_month("2025-10-25")
        # 10/01-10/24 (金) まで = 18日
        assert result == 18

    def test_elapsed_weekdays_from_first_day(self):
        """月初日の経過平日"""
        # 2025-10-01 (水)
        result = get_elapsed_weekdays_in_month("2025-10-01")
        assert result == 0  # 昨日までなので0

    def test_elapsed_weekdays_from_second_day(self):
        """2日目の経過平日"""
        # 2025-10-02 (木)
        result = get_elapsed_weekdays_in_month("2025-10-02")
        assert result == 1  # 10/01 (水) のみ

    def test_elapsed_weekdays_from_last_day(self):
        """月末日の経過平日"""
        # 2025-10-31 (金)
        result = get_elapsed_weekdays_in_month("2025-10-31")
        # 10/01-10/30 (木) まで = 22日
        assert result == 22

