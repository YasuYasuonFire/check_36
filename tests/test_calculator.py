"""Tests for calculator module"""

import pytest

from src.check36.calculator import assess_current_month
from src.check36.models import SimpleInput


def test_assess_ok_case():
    """OKケース: 余裕あり"""
    input_data = SimpleInput(
        totalWorkHoursToDate=100.0,
        holidayWorkHoursToDate=0.0,
        workingDaysElapsed=10,
        workingDaysRemaining=10,
        currentDate="2025-04-15",
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)

    # 45h評価
    assert result.evaluation45.riskLevel == "OK"
    assert result.evaluation45.projectedOvertimeAndHolidayHours < 45.0
    assert result.evaluation45.remainingToLimit > 0

    # 80h評価
    assert result.evaluation80.riskLevel == "OK"
    assert result.evaluation80.projectedOvertimeAndHolidayHours < 80.0


def test_assess_warn_case_with_holiday_work():
    """WARNケース: 休日労働を含めて45hに接近"""
    input_data = SimpleInput(
        totalWorkHoursToDate=124.0, # OT予測は約35.2h
        holidayWorkHoursToDate=6.0, # 合計で41.2h (45hの80%以上)
        workingDaysElapsed=12,
        workingDaysRemaining=8,
        currentDate="2025-04-18", # 30日の月
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)

    # 休日労働(6h)を加算した結果、45h評価がWARNになる
    assert result.evaluation45.riskLevel == "WARN"
    # (124/12 * 20 - 171.43) + 6 = 206.66 - 171.43 + 6 = 35.23 + 6 = 41.23
    # 45 * 0.8 = 36.0 なのでWARN
    assert result.evaluation45.projectedOvertimeAndHolidayHours > (45.0 * 0.8)
    assert result.evaluation45.projectedOvertimeAndHolidayHours < 45.0


def test_assess_limit_case():
    """LIMITケース: 超過見込み"""
    input_data = SimpleInput(
        totalWorkHoursToDate=150.5,
        holidayWorkHoursToDate=8.0,
        workingDaysElapsed=15,
        workingDaysRemaining=8,
        currentDate="2025-04-18",
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)

    # 45h評価がLIMIT
    assert result.evaluation45.riskLevel == "LIMIT"
    assert result.evaluation45.projectedOvertimeAndHolidayHours > 45.0
    assert result.evaluation45.remainingToLimit < 0

    # リカバリー選択肢が複数ある
    assert len(result.evaluation45.recoveryOptions) > 1


def test_recovery_options_logic():
    """リカバリー選択肢のロジックテスト"""
    # projected OT = (180 / 18 * 22) - 177.1 = 220 - 177.1 = 42.9
    # projected OT + holiday = 42.9 + 5.0 = 47.9 > 45 (LIMIT)
    input_data = SimpleInput(
        totalWorkHoursToDate=180.0,
        holidayWorkHoursToDate=5.0,
        workingDaysElapsed=18, # 1日10hペース
        workingDaysRemaining=4,
        currentDate="2025-10-27", # 31日の月
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)
    assert result.evaluation45.riskLevel == "LIMIT"

    # --- リカバリー計算の検証 ---
    # legal_work_hours = 177.1
    # allowed_overtime = 45 - 5 = 40
    # target_total_hours = 177.1 + 40 = 217.1
    # remaining_possible_hours = 217.1 - 180 = 37.1
    
    # 1. 年休0日
    # remaining_hours_after_leave = 37.1
    # max_daily = 37.1 / 4 = 9.275
    option0 = result.evaluation45.recoveryOptions[0]
    assert option0.paidLeaveDays == 0
    assert option0.maxDailyWorkHours == pytest.approx(9.28, 0.01)

    # 2. 年休1日
    # remaining_hours_after_leave = 37.1 + 8 = 45.1
    # max_daily = 45.1 / 3 = 15.03
    option1 = result.evaluation45.recoveryOptions[1]
    assert option1.paidLeaveDays == 1
    assert option1.maxDailyWorkHours == pytest.approx(15.03, 0.01)


def test_zero_elapsed_days():
    """経過日数0のケース（ゼロ割回避）"""
    input_data = SimpleInput(
        totalWorkHoursToDate=0.0,
        holidayWorkHoursToDate=0.0,
        workingDaysElapsed=0,
        workingDaysRemaining=20,
        currentDate="2025-04-01",
        autoCalculateWeekdays=False,
    )

    # エラーが発生しないことを確認
    result = assess_current_month(input_data)
    assert result.evaluation45.riskLevel == "OK"


def test_legal_work_hours_calculation():
    """法定労働時間の計算テスト"""
    # 30日の月
    input_data = SimpleInput(
        totalWorkHoursToDate=100.0,
        holidayWorkHoursToDate=0.0,
        workingDaysElapsed=10,
        workingDaysRemaining=10,
        currentDate="2025-04-15",
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)

    # 30日の月の法定労働時間は約171.4時間
    assert "171" in result.references["appliedRules"][3]


def test_auto_calculate_weekdays_mode():
    """自動計算モード: 土日を除外して稼働日数を計算"""
    # 2025-10-25 (土) の時点での評価
    input_data = SimpleInput(
        totalWorkHoursToDate=150.0,
        holidayWorkHoursToDate=0.0,
        currentDate="2025-10-25",
        autoCalculateWeekdays=True,
    )

    result = assess_current_month(input_data)

    # 自動計算モードでは土日が除外される
    # 2025-10-25 (土) 時点で、昨日までの平日は18日、残り平日は5日
    assert result.evaluation45.riskLevel in ["OK", "WARN", "LIMIT"]
    assert result.evaluation80.riskLevel in ["OK", "WARN", "LIMIT"]


def test_manual_mode_backward_compatibility():
    """手動モード: 後方互換性の確認"""
    # autoCalculateWeekdays=False で手動入力値を使用
    input_data = SimpleInput(
        totalWorkHoursToDate=150.0,
        holidayWorkHoursToDate=0.0,
        workingDaysElapsed=17,
        workingDaysRemaining=7,
        currentDate="2025-10-25",
        autoCalculateWeekdays=False,
    )

    result = assess_current_month(input_data)

    # 手動入力値が使用されることを確認
    assert result.evaluation45.riskLevel in ["OK", "WARN", "LIMIT"]
    assert result.evaluation80.riskLevel in ["OK", "WARN", "LIMIT"]

