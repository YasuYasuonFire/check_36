# Changelog v2.0 - 営業日自動計算機能

## リリース日
2025-10-25

## 概要
土日を除外した営業日（平日）を自動計算する機能を追加しました。これにより、ユーザーは稼働日数を手動で数える必要がなくなり、より簡単に36協定の判定を行えるようになりました。

## 新機能

### 1. 営業日（平日）自動計算機能
- 日付から自動的に土日を除外して稼働日数を計算
- `workingDaysElapsed`（経過稼働日数）と`workingDaysRemaining`（残り稼働日数）の入力が不要に
- デフォルトで有効（`autoCalculateWeekdays=true`）

### 2. 新しいユーティリティ関数
- `count_weekdays()`: 指定期間内の平日数をカウント
- `get_remaining_weekdays_in_month()`: 今日から月末までの平日数を取得
- `get_elapsed_weekdays_in_month()`: 月初から昨日までの平日数を取得

### 3. 柔軟な入力モード
- **自動計算モード**（デフォルト）: 土日を除外して自動計算
- **手動入力モード**: 従来通り稼働日数を手動で指定可能

## 変更内容

### 修正されたファイル

#### `src/check36/utils.py`
- `count_weekdays()` 関数を追加
- `get_remaining_weekdays_in_month()` 関数を追加
- `get_elapsed_weekdays_in_month()` 関数を追加

#### `src/check36/models.py`
- `SimpleInput.workingDaysElapsed` を `Optional[int]` に変更
- `SimpleInput.workingDaysRemaining` を `Optional[int]` に変更
- `SimpleInput.autoCalculateWeekdays` フィールドを追加（デフォルト: `True`）

#### `src/check36/calculator.py`
- 自動計算モードと手動入力モードの切り替えロジックを追加
- 稼働日数の決定ロジックを更新

#### `src/check36/server.py`
- MCPツールのパラメータを更新
- `workingDaysElapsed` と `workingDaysRemaining` をオプショナルに変更
- `autoCalculateWeekdays` パラメータを追加

#### `README.md`
- 新機能の説明を追加
- 使用例を更新（自動計算モードと手動入力モード）
- 入力パラメータの説明を更新

### 新規ファイル

#### `docs/WEEKDAY_CALCULATION.md`
- 営業日自動計算機能の詳細ドキュメント
- 使用例とテストケース
- 移行ガイド

#### `tests/test_utils.py`
- 営業日計算関数の包括的なテストスイート
- 16個の新しいテストケース

#### `src/check36/__main__.py`
- `python -m check36` でサーバーを起動できるエントリーポイント

## 使用例

### 自動計算モード（推奨）

```python
from check36.models import SimpleInput
from check36.calculator import assess_current_month

# 稼働日数は自動計算される
input_data = SimpleInput(
    totalWorkHoursToDate=150.0,
    holidayWorkHoursToDate=0.0,
    currentDate="2025-10-25",
)

result = assess_current_month(input_data)
```

### 手動入力モード（後方互換性）

```python
# 従来通りの使い方
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

## 後方互換性

既存のコードは、`autoCalculateWeekdays=False` を指定することで、そのまま動作します。

## テスト

- 全24個のテストケースがパス
- 新規テスト: 16個（営業日計算関連）
- 既存テスト: 8個（後方互換性を確認）

## 制限事項

- 現在のバージョンでは祝日は考慮されません
- 全ての平日（月〜金）が稼働日としてカウントされます
- 祝日を考慮したい場合は、手動入力モードを使用してください

## 今後の拡張予定

- 祝日データの統合
- 会社独自の休業日設定
- 地域別の祝日対応

## 移行ガイド

詳細は `docs/WEEKDAY_CALCULATION.md` を参照してください。

## コミット履歴

1. `feat: 土日を除外した営業日（平日）自動計算機能を追加`
   - 営業日計算関数の実装
   - モデルとロジックの更新
   - テストとドキュメントの追加

2. `fix: MCPツールのパラメータをオプショナルに変更`
   - MCPツールインターフェースの更新
   - パラメータのドキュメント更新

## 貢献者

- 実装: AI Assistant
- レビュー: yasuyasu

