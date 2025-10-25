"""Core calculation logic for 36 Agreement compliance check"""

import math
from typing import Literal

from .models import LimitAssessment, RecoveryOption, SimpleAssessmentOutput, SimpleInput
from .utils import (
    calculate_legal_work_hours,
    get_current_date,
    get_days_in_month,
    get_elapsed_weekdays_in_month,
    get_remaining_weekdays_in_month,
    parse_date,
)


def assess_current_month(input_data: SimpleInput) -> SimpleAssessmentOutput:
    """現在の月の36協定上限到達リスクを評価"""

    # 日付の取得・パース
    current_date_str = input_data.currentDate or get_current_date()
    year, month, _ = parse_date(current_date_str)
    
    # 稼働日数の決定（自動計算 or 手動入力）
    if input_data.autoCalculateWeekdays:
        # 土日を除外して自動計算
        working_days_elapsed = get_elapsed_weekdays_in_month(current_date_str)
        working_days_remaining = get_remaining_weekdays_in_month(current_date_str)
    else:
        # 手動入力値を使用（後方互換性）
        working_days_elapsed = input_data.workingDaysElapsed or 0
        working_days_remaining = input_data.workingDaysRemaining or 0

    # 月の情報
    days_in_month = get_days_in_month(year, month)
    legal_work_hours = calculate_legal_work_hours(days_in_month)

    # 予測計算
    avg_daily_hours = _calculate_average_daily_hours(
        input_data.totalWorkHoursToDate, working_days_elapsed
    )
    projected_total_hours = input_data.totalWorkHoursToDate + (
        working_days_remaining * avg_daily_hours
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
        projected_overtime=projected_overtime_with_holiday, # 休日労働を含める
        holiday_work_hours_to_date=input_data.holidayWorkHoursToDate, # リカバリー計算用に渡す
        legal_work_hours=legal_work_hours,
        working_days_remaining=working_days_remaining,
        warn_ratio=warn_ratio,
    )

    # 80h評価（休日含む）
    evaluation80 = _assess_limit(
        limit=80.0,
        total_work_hours_to_date=input_data.totalWorkHoursToDate,
        projected_total_hours=projected_total_hours,
        projected_overtime=projected_overtime_with_holiday,
        holiday_work_hours_to_date=input_data.holidayWorkHoursToDate, # リカバリー計算用に渡す
        legal_work_hours=legal_work_hours,
        working_days_remaining=working_days_remaining,
        warn_ratio=warn_ratio,
    )

    # 適用ルール
    applied_rules = [
        "方針: 安全側に倒すため、45h/80h評価ともに「時間外+休日」で評価",
        "月45時間上限（時間外労働+休日労働）",
        "80時間基準（時間外労働+休日労働、簡易単月評価）",
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
    holiday_work_hours_to_date: float,
    legal_work_hours: float,
    working_days_remaining: int,
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
        holiday_work_hours_to_date=holiday_work_hours_to_date,
        legal_work_hours=legal_work_hours,
        working_days_remaining=working_days_remaining,
    )

    return LimitAssessment(
        limit=limit,
        totalWorkHoursToDate=total_work_hours_to_date,
        projectedTotalWorkHours=projected_total_hours,
        projectedOvertimeAndHolidayHours=projected_overtime,
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
    holiday_work_hours_to_date: float,
    legal_work_hours: float,
    working_days_remaining: int,
) -> list[RecoveryOption]:
    """リカバリー選択肢を生成"""

    options: list[RecoveryOption] = []
    
    # 45h/80hリミットから、現在までの休日労働時間を除いたものが、
    # 残り期間の時間外労働で許容される上限となる
    allowed_overtime_for_remaining_days = limit - holiday_work_hours_to_date

    # 上限達成に必要な総労働時間
    target_total_hours = legal_work_hours + allowed_overtime_for_remaining_days

    # 残り期間で可能な総労働時間
    remaining_possible_hours = target_total_hours - total_work_hours_to_date

    # 年休取得による削減時間（1日あたり8時間固定）
    PAID_LEAVE_REDUCTION_HOURS = 8.0

    # 年休0〜5日のパターンを生成
    for paid_leave_days in range(min(6, working_days_remaining + 1)):
        actual_working_days = working_days_remaining - paid_leave_days

        if actual_working_days <= 0 and remaining_possible_hours < 0:
            # 稼働日数がなく、かつ既に上限を超過している場合は表示しない
            if paid_leave_days == 0: # 年休0日でもダメな場合のみループを抜ける
                options.append(
                    RecoveryOption(
                        paidLeaveDays=0,
                        maxDailyWorkHours=0.0,
                        description=f"年休なし：残り稼働日0日。既に{abs(remaining_possible_hours):.2f}時間超過しています。",
                    )
                )
            break

        # 年休取得で労働時間がマイナスになる場合も考慮
        remaining_hours_after_leave = remaining_possible_hours + (paid_leave_days * PAID_LEAVE_REDUCTION_HOURS)
        
        if actual_working_days <= 0:
            if remaining_hours_after_leave >= 0:
                # 休みきればOK
                 options.append(
                    RecoveryOption(
                        paidLeaveDays=paid_leave_days,
                        maxDailyWorkHours=0.0,
                        description=f"年休{paid_leave_days}日取得：残り稼働日なし。これで上限内に収まります。",
                    )
                )
                 break
            else:
                continue


        # 1日あたり上限
        max_daily_hours = remaining_hours_after_leave / actual_working_days

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

