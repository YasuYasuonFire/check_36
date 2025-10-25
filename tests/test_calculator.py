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
    )

    result = assess_current_month(input_data)

    # 45h評価
    assert result.evaluation45.riskLevel == "OK"
    assert result.evaluation45.projectedOvertimeHours < 45.0
    assert result.evaluation45.remainingToLimit > 0

    # 80h評価
    assert result.evaluation80.riskLevel == "OK"
    assert result.evaluation80.projectedOvertimeHours < 80.0


def test_assess_warn_case():
    """WARNケース: 80%接近"""
    input_data = SimpleInput(
        totalWorkHoursToDate=140.0,
        holidayWorkHoursToDate=5.0,
        workingDaysElapsed=12,
        workingDaysRemaining=8,
        currentDate="2025-04-18",
    )

    result = assess_current_month(input_data)

    # 45h評価がWARNまたはLIMIT
    assert result.evaluation45.riskLevel in ["WARN", "LIMIT"]


def test_assess_limit_case():
    """LIMITケース: 超過見込み"""
    input_data = SimpleInput(
        totalWorkHoursToDate=150.5,
        holidayWorkHoursToDate=8.0,
        workingDaysElapsed=15,
        workingDaysRemaining=8,
        currentDate="2025-04-18",
    )

    result = assess_current_month(input_data)

    # 45h評価がLIMIT
    assert result.evaluation45.riskLevel == "LIMIT"
    assert result.evaluation45.projectedOvertimeHours > 45.0
    assert result.evaluation45.remainingToLimit < 0

    # リカバリー選択肢が複数ある
    assert len(result.evaluation45.recoveryOptions) > 1


def test_recovery_options_generation():
    """リカバリー選択肢の生成テスト"""
    input_data = SimpleInput(
        totalWorkHoursToDate=150.0,
        holidayWorkHoursToDate=5.0,
        workingDaysElapsed=15,
        workingDaysRemaining=8,
        currentDate="2025-04-18",
    )

    result = assess_current_month(input_data)

    # 年休0日のオプションが存在
    assert any(opt.paidLeaveDays == 0 for opt in result.evaluation45.recoveryOptions)

    # 各オプションに説明文がある
    for opt in result.evaluation45.recoveryOptions:
        assert opt.description
        assert "日間" in opt.description
        assert "時間以内" in opt.description


def test_zero_elapsed_days():
    """経過日数0のケース（ゼロ割回避）"""
    input_data = SimpleInput(
        totalWorkHoursToDate=0.0,
        holidayWorkHoursToDate=0.0,
        workingDaysElapsed=0,
        workingDaysRemaining=20,
        currentDate="2025-04-01",
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
    )

    result = assess_current_month(input_data)

    # 30日の月の法定労働時間は約171.4時間
    assert "171" in result.references["appliedRules"][2]

