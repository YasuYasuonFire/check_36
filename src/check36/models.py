"""Pydantic models for input/output validation"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class ConfigModel(BaseModel):
    """設定モデル"""

    thresholds: dict[str, float] = Field(default_factory=lambda: {"warnRatio": 0.8})


class SimpleInput(BaseModel):
    """シンプル入力モデル"""

    totalWorkHoursToDate: float = Field(ge=0, description="前日までの総労働時間")
    holidayWorkHoursToDate: float = Field(ge=0, description="前日までの休日労働時間")
    workingDaysElapsed: Optional[int] = Field(None, ge=0, description="前日までに働いた日数（省略時は自動計算）")
    workingDaysRemaining: Optional[int] = Field(None, ge=0, description="今日を含む残りの稼働日数（省略時は自動計算）")
    currentDate: Optional[str] = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="評価基準日（YYYY-MM-DD）"
    )
    autoCalculateWeekdays: bool = Field(
        default=True, description="土日を除外して自動計算するか（True: 平日のみ、False: 手動入力値を使用）"
    )
    config: Optional[ConfigModel] = None

    @field_validator("currentDate")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """日付形式の検証"""
        if v is None:
            return v
        # 簡易的な検証（実際の日付妥当性は後でチェック）
        parts = v.split("-")
        if len(parts) != 3:
            raise ValueError("Invalid date format")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= month <= 12 and 1 <= day <= 31):
            raise ValueError("Invalid date values")
        return v


class RecoveryOption(BaseModel):
    """リカバリー選択肢"""

    paidLeaveDays: int = Field(ge=0, description="年休取得日数")
    maxDailyWorkHours: float = Field(ge=0, description="1日あたり上限総労働時間")
    description: str = Field(description="説明文")


class LimitAssessment(BaseModel):
    """上限評価"""

    limit: float = Field(description="上限値")
    totalWorkHoursToDate: float = Field(description="昨日までの総労働時間")
    projectedTotalWorkHours: float = Field(description="月末予測の総労働時間")
    projectedOvertimeHours: float = Field(description="月末予測の時間外労働")
    remainingToLimit: float = Field(description="上限までの残り（負=超過見込み）")
    riskLevel: Literal["OK", "WARN", "LIMIT"] = Field(description="リスクレベル")
    recoveryOptions: list[RecoveryOption] = Field(description="リカバリー選択肢")


class SimpleAssessmentOutput(BaseModel):
    """評価出力"""

    evaluation45: LimitAssessment = Field(description="45h上限評価")
    evaluation80: LimitAssessment = Field(description="80h基準評価")
    references: dict[str, list[str]] = Field(description="適用ルール")

