# 営業日（平日）自動計算機能

## 概要

バージョン 2.0 から、土日を除外した営業日（平日）を自動計算する機能が追加されました。

## 機能説明

### 自動計算モード（デフォルト）

`autoCalculateWeekdays=True`（デフォルト）の場合、以下が自動計算されます：

- **経過稼働日数**: 月初から昨日までの平日数（土日を除く）
- **残り稼働日数**: 今日から月末までの平日数（土日を除く）

### 手動入力モード（後方互換性）

`autoCalculateWeekdays=False` の場合、従来通り手動で入力した値を使用します。

## 使用例

### 例1: 自動計算モード（推奨）

```python
from check36.models import SimpleInput
from check36.calculator import assess_current_month

# 土日を除外して自動計算
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    currentDate="2025-10-25",  # 土曜日
    autoCalculateWeekdays=True,  # デフォルトなので省略可能
)

result = assess_current_month(input_data)
```

この場合：
- 2025-10-25（土）時点で
- 昨日までの平日数: 18日（10/1-10/24の平日）
- 残りの平日数: 5日（10/27-10/31の平日）
- が自動計算されます

### 例2: 手動入力モード（後方互換性）

```python
# 手動で稼働日数を指定
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    workingDaysElapsed=17,
    workingDaysRemaining=7,
    currentDate="2025-10-25",
    autoCalculateWeekdays=False,
)

result = assess_current_month(input_data)
```

### 例3: MCPツールから使用

```json
{
  "totalWorkHoursToDate": 150.0,
  "holidayWorkHoursToDate": 0.0,
  "currentDate": "2025-10-25"
}
```

`autoCalculateWeekdays` を省略すると、デフォルトで `True` となり、自動計算されます。

## 計算ロジック

### 平日のカウント方法

- 月曜日〜金曜日を平日としてカウント
- 土曜日・日曜日は除外
- 祝日は考慮しない（将来的に拡張可能）

### 経過平日数の計算

```
月初日（1日）から昨日までの期間内の平日数
```

例: 2025-10-25（土）の場合
- 対象期間: 2025-10-01 〜 2025-10-24
- 平日数: 18日

### 残り平日数の計算

```
今日から月末までの期間内の平日数
```

例: 2025-10-25（土）の場合
- 対象期間: 2025-10-25 〜 2025-10-31
- 平日数: 5日（10/27-10/31）

## 注意事項

### 祝日について

現在のバージョンでは、祝日は考慮されません。全ての平日（月〜金）が稼働日としてカウントされます。

祝日を考慮したい場合は、`autoCalculateWeekdays=False` を指定し、手動で稼働日数を入力してください。

### 月初・月末の扱い

- **月初日（1日）**: 経過稼働日数は0（昨日までなので）
- **月末日**: 残り稼働日数は1（今日のみ）

### 土日の扱い

- **土曜日**: その日自体は稼働日としてカウントされない
- **日曜日**: その日自体は稼働日としてカウントされない

## テストケース

詳細なテストケースは `tests/test_utils.py` を参照してください。

### 主要なテストシナリオ

1. 1週間の平日カウント（月〜金）
2. 週末を含む期間の平日カウント
3. 土曜日から土曜日までのカウント
4. 1日のみ（平日・週末）
5. 1ヶ月全体のカウント
6. 月初・月末の境界ケース

## 移行ガイド

### 既存コードからの移行

既存のコードは、`autoCalculateWeekdays=False` を追加することで、そのまま動作します。

```python
# 既存コード（v1.x）
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    workingDaysElapsed=17,
    workingDaysRemaining=7,
    currentDate="2025-10-25",
)

# 移行後（v2.x）- 後方互換性を保つ
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    workingDaysElapsed=17,
    workingDaysRemaining=7,
    currentDate="2025-10-25",
    autoCalculateWeekdays=False,  # これを追加
)
```

### 新機能を活用する場合

稼働日数の指定を省略し、自動計算に任せます。

```python
# 新しい方法（推奨）
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    currentDate="2025-10-25",
    # workingDaysElapsed と workingDaysRemaining は不要
    # autoCalculateWeekdays=True がデフォルト
)
```

## 今後の拡張予定

- 祝日データの統合
- 会社独自の休業日設定
- 地域別の祝日対応

