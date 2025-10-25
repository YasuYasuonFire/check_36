# データモデル（シンプル入力版）

- 入力
  - MonthlySimpleInput {
      overtimeHoursToDate: number,
      holidayWorkHoursToDate: number,
      currentDate?: string,
      workingDaysRemaining?: number,
      config?: { thresholds?: { warnRatio?: number } }
    }

- 出力
  - SimpleAssessmentOutput {
      evaluation45: LimitAssessment,
      evaluation80: LimitAssessment,
      references: { appliedRules: string[] }
    }
  - LimitAssessment {
      projectedOvertimeAndHolidayHours: number, // 予測時間外+休日
      remainingToLimit: number,
      riskLevel: "OK"|"WARN"|"LIMIT",
      recoveryOptions: object[] // 詳細はMCP I/F仕様書を参照
    }

- テンプレート
  - templates/simple_input.sample.json
