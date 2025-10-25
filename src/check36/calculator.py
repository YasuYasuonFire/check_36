"""Core calculation logic for 36 Agreement compliance check"""

import math
from typing import Literal

from .models import LimitAssessment, RecoveryOption, SimpleAssessmentOutput, SimpleInput
from .utils import calculate_legal_work_hours, get_current_date, get_days_in_month, parse_date


def assess_current_month(input_data: SimpleInput) -> SimpleAssessmentOutput:
    """現在の月の36協定上限到達リスクを評価"""

    # 日付の取得・パース
    current_date_str = input_data.currentDate or get_current_date()
    year, month, _ = parse_date(current_date_str)

    # 月の情報
    days_in_month = get_days_in_month(year, month)
    legal_work_hours = calculate_legal_work_hours(days_in_month)

    # 予測計算
    avg_daily_hours = _calculate_average_daily_hours(
        input_data.totalWorkHoursToDate, input_data.workingDaysElapsed
    )
    projected_total_hours = input_data.totalWorkHoursToDate + (
        input_data.workingDaysRemaining * avg_daily_hours
    )
    projected_overtime = projected_total_hours - legal_work_hours
    projected_overtime_with_holiday = projected_overtime + input_data.holidayWorkHoursToDate

    # 閾値
    warn_ratio = 0.8
    if input_data.config and input_data.config.thresholds:
        warn_ratio = input_data.config.thresholds.get("warnRatio", 0.8)

    # 45h評価
    evaluation45 = _assess_limit(
        limit=45.0,
        total_work_hours_to_date=input_data.totalWorkHoursToDate,
        projected_total_hours=projected_total_hours,
        projected_overtime=projected_overtime,
        legal_work_hours=legal_work_hours,
        working_days_remaining=input_data.workingDaysRemaining,
        avg_daily_hours=avg_daily_hours,
        warn_ratio=warn_ratio,
    )

    # 80h評価（休日含む）
    evaluation80 = _assess_limit(
        limit=80.0,
        total_work_hours_to_date=input_data.totalWorkHoursToDate,
        projected_total_hours=projected_total_hours,
        projected_overtime=projected_overtime_with_holiday,
        legal_work_hours=legal_work_hours,
        working_days_remaining=input_data.workingDaysRemaining,
        avg_daily_hours=avg_daily_hours,
        warn_ratio=warn_ratio,
    )

    # 適用ルール
    applied_rules = [
        "月45時間上限（時間外のみ）",
        "80時間基準（休日労働含む、簡易単月評価）",
        f"月の法定労働時間: {legal_work_hours:.1f}時間（{days_in_month}日の月）",
    ]

    return SimpleAssessmentOutput(
        evaluation45=evaluation45, evaluation80=evaluation80, references={"appliedRules": applied_rules}
    )


def _calculate_average_daily_hours(total_hours: float, elapsed_days: int) -> float:
    """1日あたり平均労働時間を計算"""
    if elapsed_days == 0:
        return 8.0  # デフォルト値
    return total_hours / elapsed_days


def _assess_limit(
    limit: float,
    total_work_hours_to_date: float,
    projected_total_hours: float,
    projected_overtime: float,
    legal_work_hours: float,
    working_days_remaining: int,
    avg_daily_hours: float,
    warn_ratio: float,
) -> LimitAssessment:
    """上限に対する評価を実施"""

    # 残余計算
    remaining_to_limit = limit - projected_overtime

    # リスクレベル判定
    risk_level = _determine_risk_level(projected_overtime, limit, warn_ratio)

    # リカバリー選択肢生成
    recovery_options = _generate_recovery_options(
        limit=limit,
        total_work_hours_to_date=total_work_hours_to_date,
        projected_overtime=projected_overtime,
        legal_work_hours=legal_work_hours,
        working_days_remaining=working_days_remaining,
        avg_daily_hours=avg_daily_hours,
    )

    return LimitAssessment(
        limit=limit,
        totalWorkHoursToDate=total_work_hours_to_date,
        projectedTotalWorkHours=projected_total_hours,
        projectedOvertimeHours=projected_overtime,
        remainingToLimit=remaining_to_limit,
        riskLevel=risk_level,
        recoveryOptions=recovery_options,
    )


def _determine_risk_level(
    projected_overtime: float, limit: float, warn_ratio: float
) -> Literal["OK", "WARN", "LIMIT"]:
    """リスクレベルを判定"""
    if projected_overtime >= limit:
        return "LIMIT"
    elif projected_overtime >= limit * warn_ratio:
        return "WARN"
    else:
        return "OK"


def _generate_recovery_options(
    limit: float,
    total_work_hours_to_date: float,
    projected_overtime: float,
    legal_work_hours: float,
    working_days_remaining: int,
    avg_daily_hours: float,
) -> list[RecoveryOption]:
    """リカバリー選択肢を生成"""

    options: list[RecoveryOption] = []

    # 上限達成に必要な総労働時間
    target_total_hours = legal_work_hours + limit

    # 残り期間で可能な総労働時間
    remaining_possible_hours = target_total_hours - total_work_hours_to_date

    # 年休0〜5日のパターンを生成
    for paid_leave_days in range(min(6, working_days_remaining + 1)):
        actual_working_days = working_days_remaining - paid_leave_days

        if actual_working_days <= 0:
            # 実働日数が0以下の場合はスキップ
            continue

        # 年休取得による削減
        reduced_hours = remaining_possible_hours - (paid_leave_days * avg_daily_hours)

        # 1日あたり上限
        max_daily_hours = reduced_hours / actual_working_days

        if max_daily_hours < 0:
            max_daily_hours = 0.0

        # 説明文
        if paid_leave_days == 0:
            description = f"年休なし：残り{actual_working_days}日間、1日あたり{max_daily_hours:.2f}時間以内"
        else:
            description = f"年休{paid_leave_days}日取得：残り{actual_working_days}日間、1日あたり{max_daily_hours:.2f}時間以内"

        options.append(
            RecoveryOption(
                paidLeaveDays=paid_leave_days,
                maxDailyWorkHours=round(max_daily_hours, 2),
                description=description,
            )
        )

        # 超過見込みがない場合は1パターンのみ
        if projected_overtime < limit and paid_leave_days == 0:
            break

    return options

