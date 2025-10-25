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
      limit: number,                      // 上限値（45）
      totalWorkHoursToDate: number,       // 昨日までの総労働時間（入力値）
      projectedTotalWorkHours: number,    // 月末予測の総労働時間
      projectedOvertimeAndHolidayHours: number, // 月末予測の時間外+休日労働
      remainingToLimit: number,           // 上限までの残り（負=超過見込み）
      riskLevel: "OK"|"WARN"|"LIMIT",
      recoveryOptions: [
        {
          paidLeaveDays: number,
          maxDailyWorkHours: number,      // 1日あたり上限総労働時間
          description: string             // "年休N日取得：残りX日間、1日あたりY時間以内"
        }
      ]
    }
  - evaluation80: {
      limit: number,                      // 上限値（80）
      totalWorkHoursToDate: number,       // 昨日までの総労働時間（入力値）
      projectedTotalWorkHours: number,    // 月末予測の総労働時間
      projectedOvertimeAndHolidayHours: number, // 月末予測の時間外+休日労働
      remainingToLimit: number,           // 上限までの残り（負=超過見込み）
      riskLevel: "OK"|"WARN"|"LIMIT",
      recoveryOptions: [
        {
          paidLeaveDays: number,
          maxDailyWorkHours: number,      // 1日あたり上限総労働時間
          description: string             // "年休N日取得：残りX日間、1日あたりY時間以内"
        }
      ]
    }
  - references: { appliedRules: string[] }
  
  ※ 方針: 安全側に倒すため、45h評価・80h評価ともに「時間外+休日」の合算値で評価する
  ※ フレックス制度対応：「現在の時間外」は算出せず、予測ベースで評価

- 備考
  - 80hは簡易単月比較。将来は複数月平均評価へ拡張予定。
