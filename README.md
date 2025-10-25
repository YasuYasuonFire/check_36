# 36協定チェック用 MCP サーバー

本リポジトリは、日本の36協定（労基法第36条）に関する月次の上限到達リスクを評価し、リカバリー策（年休取得・1日あたり稼働上限設定）を提案する MCP サーバーです。

## 概要

現在の月の時間外労働・休日労働の累計時間を入力すると、以下の2つの上限に対する到達予測とリカバリー提案を出力します：
- **月45時間上限**（時間外労働のみ）
- **80時間基準**（時間外+休日労働、簡易単月評価）

## 使用例

### 入力例

Claude Desktop や MCP Inspector で以下のように入力します：

```json
{
  "totalWorkHoursToDate": 150.5,
  "holidayWorkHoursToDate": 8.0,
  "workingDaysElapsed": 15,
  "workingDaysRemaining": 8,
  "currentDate": "2025-04-18"
}
```

**入力項目の説明**
- `totalWorkHoursToDate`: **前日（昨日）までの**総労働時間 累計（時間）【必須】
  - 勤怠システムの「総労働時間」をそのまま入力
  - 時間外・休日を含む全ての労働時間
  - ⚠️ 今日の分は含めない（確定値のみ）
- `holidayWorkHoursToDate`: **前日までの**休日労働 累計（時間）【必須】
- `workingDaysElapsed`: **前日までに**働いた日数【必須】
  - 月初から昨日までの実際に働いた日数
- `workingDaysRemaining`: **今日を含む**月末までの残り稼働日数【必須】
  - 今日以降、月末までに働く予定の日数
- `currentDate`: 評価基準日（YYYY-MM-DD形式、省略時は今日）【任意】
  - 月の暦日数算出に使用

**計算の仕組み**
- 月の法定労働時間を自動計算：`(月の暦日数 ÷ 7) × 40時間`
  - 例：30日の月 → 171.4時間
- 時間外労働を自動算出：`総労働時間 - 法定労働時間`
- 月末予測：`昨日までの累計 + (残り日数 × 1日平均労働時間)`
  - 1日平均 = 昨日までの累計 ÷ 経過日数

### 出力例

```json
{
  "evaluation45": {
    "limit": 45,
    "currentHours": 32.5,
    "projectedHours": 48.3,
    "remainingHours": -3.3,
    "riskLevel": "LIMIT",
    "recoveryOptions": [
      {
        "paidLeaveDays": 0,
        "maxDailyOvertimeHours": 1.56,
        "description": "年休なし：残り8日間、1日あたり1.56時間以内"
      },
      {
        "paidLeaveDays": 1,
        "maxDailyOvertimeHours": 2.34,
        "description": "年休1日取得：残り7日間、1日あたり2.34時間以内"
      },
      {
        "paidLeaveDays": 2,
        "maxDailyOvertimeHours": 3.42,
        "description": "年休2日取得：残り6日間、1日あたり3.42時間以内"
      }
    ]
  },
  "evaluation80": {
    "limit": 80,
    "currentHours": 40.5,
    "projectedHours": 60.8,
    "remainingHours": 19.2,
    "riskLevel": "OK",
    "recoveryOptions": [
      {
        "paidLeaveDays": 0,
        "maxDailyOvertimeHours": 4.94,
        "description": "年休なし：残り8日間、1日あたり4.94時間以内"
      }
    ]
  },
  "references": {
    "appliedRules": [
      "月45時間上限（時間外のみ）",
      "80時間基準（休日労働含む、簡易単月評価）"
    ]
  }
}
```

**出力項目の説明**

各評価（`evaluation45`, `evaluation80`）には以下が含まれます：
- `limit`: 上限値（45 または 80）
- `currentHours`: 現在の累計時間
- `projectedHours`: 月末時点の予測時間数
- `remainingHours`: 上限までの残余時間（負の場合は超過見込み）
- `riskLevel`: リスクレベル
  - `OK`: 余裕あり
  - `WARN`: 上限の80%以上に到達
  - `LIMIT`: 上限超過の恐れ
- `recoveryOptions`: 複数のリカバリー選択肢（配列）
  - `paidLeaveDays`: 年休取得日数
  - `maxDailyOvertimeHours`: 残期間の1日あたり上限時間
  - `description`: 分かりやすい説明文

### 実行イメージ

Claude Desktop での会話例：

```
ユーザー: 昨日までの総労働時間が150.5時間、休日労働が8時間です。
        15日働いて、今日含めて残り8日です。上限チェックしてください。

Claude: check36.assess_current_month を実行します...

【結果】
■ 月45時間上限（時間外のみ）
- 現在: 32.5時間 / 45時間
- 月末予測: 48.3時間
- 上限まで: あと12.5時間（超過見込み -3.3時間）⚠️ LIMIT

超えないための選択肢：
  ① 年休なし：残り8日間、1日あたり1.56時間以内
  ② 年休1日取得：残り7日間、1日あたり2.34時間以内
  ③ 年休2日取得：残り6日間、1日あたり3.42時間以内

■ 80時間基準（休日労働含む）
- 現在: 40.5時間 / 80時間
- 月末予測: 60.8時間
- 上限まで: あと39.5時間（余裕あり）✅ OK

超えないための選択肢：
  ① 年休なし：残り8日間、1日あたり4.94時間以内

【アドバイス】
このペースだと月45時間を超過する見込みです。
年休を1〜2日取得するか、残り期間の時間外を抑えることをお勧めします。
```

## ドキュメント

- docs/requirements/README.md: ドキュメント目次
- docs/requirements/01_legal_baseline.md: 法的上限・用語定義
- docs/requirements/02_functional_requirements.md: 機能要件
- docs/requirements/03_nonfunctional_requirements.md: 非機能要件
- docs/requirements/04_mcp_interface_spec.md: MCP インターフェース仕様
- docs/requirements/05_data_model.md: データモデルと入力テンプレート
- docs/requirements/06_risks_constraints.md: リスク・制約
- schemas/: 入出力スキーマ
- templates/: 入力テンプレート例
- IMPLEMENTATION_PLAN.md: 実装計画
