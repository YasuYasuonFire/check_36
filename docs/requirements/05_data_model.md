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
      projectedHours: number,
      deltaToLimit: number,
      riskLevel: "OK"|"WARN"|"LIMIT",
      recovery: { suggestedPaidLeaveDays: number, suggestedMaxDailyOvertimeHours: number }
    }

- テンプレート
  - templates/simple_input.sample.json
