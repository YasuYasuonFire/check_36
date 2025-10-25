# MCP インターフェース仕様（シンプル入力版）

- ツール名
  - check36.assess_current_month

- 入力（JSON Schema 概要）
  - totalWorkHoursToDate: number ≥ 0（**前日までの**総労働時間 累計）【必須】
  - holidayWorkHoursToDate: number ≥ 0（**前日までの**休日労働 累計）【必須】
  - workingDaysElapsed: integer ≥ 0（**前日までに**働いた日数）【必須】
  - workingDaysRemaining: integer ≥ 0（**今日を含む**残りの稼働日数）【必須】
  - currentDate?: string（YYYY-MM-DD、未指定ならシステム日付）【任意】
  - config?: {
      thresholds?: { warnRatio: number = 0.8 }
    }
  
  ※ 業務時間中の使用を想定し、入力は「昨日まで」の確定値

- 出力（JSON Schema 概要）
  - evaluation45: {
      limit: number, // 上限値（45）
      currentHours: number, // 現在の累計
      projectedHours: number, // 月末予測
      remainingHours: number, // 上限までの残余（負の場合は超過見込み）
      riskLevel: "OK"|"WARN"|"LIMIT",
      recoveryOptions: [
        {
          paidLeaveDays: number,
          maxDailyOvertimeHours: number,
          description: string
        }
      ]
    }
  - evaluation80: {
      limit: number, // 上限値（80）
      currentHours: number, // 現在の累計（時間外+休日）
      projectedHours: number,
      remainingHours: number,
      riskLevel: "OK"|"WARN"|"LIMIT",
      recoveryOptions: [
        {
          paidLeaveDays: number,
          maxDailyOvertimeHours: number,
          description: string
        }
      ]
    }
  - references: { appliedRules: string[] }

- 備考
  - 80hは簡易単月比較。将来は複数月平均評価へ拡張予定。
