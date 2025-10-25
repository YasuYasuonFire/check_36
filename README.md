# 36協定チェック用 MCP サーバー

本リポジトリは、日本の36協定（労基法第36条）に関する月次の上限到達リスクを評価し、リカバリー策（年休取得・1日あたり稼働上限設定）を提案する MCP サーバーです。

## 概要

現在の月の時間外労働・休日労働の累計時間を入力すると、以下の2つの上限に対する到達予測とリカバリー提案を出力します：
- **月45時間上限**（時間外労働のみ）
- **80時間基準**（時間外+休日労働、簡易単月評価）

## 🆕 新機能（v2.0）

**営業日（平日）自動計算機能**

土日を除外した稼働日数を自動計算できるようになりました！

- `workingDaysElapsed` と `workingDaysRemaining` の入力が不要に
- 日付から自動的に平日のみをカウント
- 詳細は [営業日計算ドキュメント](docs/WEEKDAY_CALCULATION.md) を参照

## 使用例

### 入力例

#### 簡単な使い方（推奨）- 自動計算モード

```json
{
  "totalWorkHoursToDate": 150.5,
  "holidayWorkHoursToDate": 8.0,
  "currentDate": "2025-04-18"
}
```

稼働日数は自動計算されます（土日を除く平日のみカウント）。

#### 詳細な使い方 - 手動入力モード

```json
{
  "totalWorkHoursToDate": 150.5,
  "holidayWorkHoursToDate": 8.0,
  "workingDaysElapsed": 15,
  "workingDaysRemaining": 8,
  "currentDate": "2025-04-18",
  "autoCalculateWeekdays": false
}
```

**入力項目の説明**
- `totalWorkHoursToDate`: **前日（昨日）までの**総労働時間 累計（時間）【必須】
  - 勤怠システムの「総労働時間」をそのまま入力
  - 時間外・休日を含む全ての労働時間
  - ⚠️ 今日の分は含めない（確定値のみ）
- `holidayWorkHoursToDate`: **前日までの**休日労働 累計（時間）【必須】
- `workingDaysElapsed`: **前日までに**働いた日数【任意】
  - 省略時は自動計算（月初から昨日までの平日数）
  - 手動入力する場合は `autoCalculateWeekdays: false` を指定
- `workingDaysRemaining`: **今日を含む**月末までの残り稼働日数【任意】
  - 省略時は自動計算（今日から月末までの平日数）
  - 手動入力する場合は `autoCalculateWeekdays: false` を指定
- `currentDate`: 評価基準日（YYYY-MM-DD形式、省略時は今日）【任意】
  - 月の暦日数算出に使用
- `autoCalculateWeekdays`: 稼働日数の自動計算（デフォルト: true）【任意】
  - `true`: 土日を除外して自動計算
  - `false`: 手動入力値を使用

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
    "totalWorkHoursToDate": 150.5,
    "projectedTotalWorkHours": 230.7,
    "projectedOvertimeHours": 53.3,
    "remainingToLimit": -8.3,
    "riskLevel": "LIMIT",
    "recoveryOptions": [
      {
        "paidLeaveDays": 0,
        "maxDailyWorkHours": 9.56,
        "description": "年休なし：残り8日間、1日あたり9.56時間以内"
      },
      {
        "paidLeaveDays": 1,
        "maxDailyWorkHours": 10.34,
        "description": "年休1日取得：残り7日間、1日あたり10.34時間以内"
      },
      {
        "paidLeaveDays": 2,
        "maxDailyWorkHours": 11.42,
        "description": "年休2日取得：残り6日間、1日あたり11.42時間以内"
      }
    ]
  },
  "evaluation80": {
    "limit": 80,
    "totalWorkHoursToDate": 150.5,
    "projectedTotalWorkHours": 230.7,
    "projectedOvertimeHours": 61.3,
    "remainingToLimit": 18.7,
    "riskLevel": "OK",
    "recoveryOptions": [
      {
        "paidLeaveDays": 0,
        "maxDailyWorkHours": 12.94,
        "description": "年休なし：残り8日間、1日あたり12.94時間以内"
      }
    ]
  },
  "references": {
    "appliedRules": [
      "月45時間上限（時間外のみ）",
      "80時間基準（休日労働含む、簡易単月評価）",
      "月の法定労働時間: 171.4時間（30日の月）"
    ]
  }
}
```

**出力項目の説明**

各評価（`evaluation45`, `evaluation80`）には以下が含まれます：
- `limit`: 上限値（45 または 80）
- `totalWorkHoursToDate`: 昨日までの総労働時間（入力値そのまま）
- `projectedTotalWorkHours`: 月末予測の総労働時間
- `projectedOvertimeHours`: 月末予測の時間外労働（または時間外+休日）
- `remainingToLimit`: 上限までの残り時間（負の場合は超過見込み）
- `riskLevel`: リスクレベル
  - `OK`: 余裕あり
  - `WARN`: 上限の80%以上に到達
  - `LIMIT`: 上限超過の恐れ
- `recoveryOptions`: 複数のリカバリー選択肢（配列）
  - `paidLeaveDays`: 年休取得日数
  - `maxDailyWorkHours`: 残期間の1日あたり上限総労働時間
  - `description`: 分かりやすい説明文

**重要**: フレックス制度対応のため、「現在の時間外」は算出しません。予測ベースでのみ評価します。

### 実行イメージ

Claude Desktop での会話例：

```
ユーザー: 昨日までの総労働時間が150.5時間、休日労働が8時間です。
        15日働いて、今日含めて残り8日です。上限チェックしてください。

Claude: check36.assess_current_month を実行します...

【結果】
■ 月45時間上限（時間外のみ）
- 昨日までの総労働時間: 150.5時間
- 月末予測の総労働時間: 230.7時間
- 月末予測の時間外労働: 53.3時間
- 45hまでの残り: -8.3時間（超過見込み）⚠️ LIMIT

超えないための選択肢：
  ① 年休なし：残り8日間、1日あたり9.56時間以内
  ② 年休1日取得：残り7日間、1日あたり10.34時間以内
  ③ 年休2日取得：残り6日間、1日あたり11.42時間以内

■ 80時間基準（休日労働含む）
- 昨日までの総労働時間: 150.5時間
- 月末予測の総労働時間: 230.7時間
- 月末予測の時間外+休日: 61.3時間
- 80hまでの残り: 18.7時間（余裕あり）✅ OK

超えないための選択肢：
  ① 年休なし：残り8日間、1日あたり12.94時間以内

【アドバイス】
このペースだと月45時間（時間外）を超過する見込みです。
年休を1〜2日取得するか、残り期間の労働時間を1日9.56時間以内に抑えることをお勧めします。
（フレックス制度を活用して、1日の労働時間を柔軟に調整できます）
```

## セットアップ

### 必要要件
- Python 3.10以上
- pip または uv

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/YasuYasuonFire/check_36.git
cd check_36

# 依存関係をインストール（開発用含む）
pip install -e ".[dev]"

# または venv を使用
python -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
pip install -e ".[dev]"
```

### テスト実行

```bash
# 全テスト実行
pytest

# 詳細表示
pytest -v

# カバレッジ付き
pytest --cov=src/check36
```

### MCPサーバー起動

```bash
# サーバー起動
python -m src.check36.server

# または
python src/check36/server.py
```

## Claude Desktop での使用方法

### 1. リポジトリのクローン

まず、このリポジトリをクローンして、パスを確認します：

```bash
# リポジトリをクローン
git clone https://github.com/YasuYasuonFire/check_36.git
cd check_36

# 現在のパスを確認（このパスを後で使います）
pwd
# 例: /Users/username/projects/check_36
```

### 2. MCP設定ファイルに追加

`~/Library/Application Support/Claude/claude_desktop_config.json` を編集します。

**⚠️ 重要な注意点:**
- `cwd` には、**上記で確認した実際のパス**を指定してください
- `command` は、お使いのPython環境に応じて変更してください

#### パターン1: システムのPythonを使用する場合

```json
{
  "mcpServers": {
    "check36": {
      "command": "python3",
      "args": ["-m", "check36.server"],
      "cwd": "/Users/username/projects/check_36"
    }
  }
}
```

#### パターン2: pyenvを使用している場合

```json
{
  "mcpServers": {
    "check36": {
      "command": "/Users/username/.pyenv/shims/python",
      "args": ["-m", "check36.server"],
      "cwd": "/Users/username/projects/check_36"
    }
  }
}
```

pyenvのパスを確認するには：
```bash
which python
# 例: /Users/username/.pyenv/shims/python
```

#### パターン3: venv（仮想環境）を使用する場合

```json
{
  "mcpServers": {
    "check36": {
      "command": "/Users/username/projects/check_36/.venv/bin/python",
      "args": ["-m", "check36.server"],
      "cwd": "/Users/username/projects/check_36"
    }
  }
}
```

venvを作成する場合：
```bash
cd /Users/username/projects/check_36
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### パターン4: uvを使用する場合（推奨）

```json
{
  "mcpServers": {
    "check36": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/username/projects/check_36", "python", "-m", "check36.server"],
      "cwd": "/Users/username/projects/check_36"
    }
  }
}
```

uvを使う場合の準備：
```bash
# uvのインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトディレクトリで依存関係をインストール
cd /Users/username/projects/check_36
uv sync
```

### 3. 設定の確認ポイント

✅ **必ず確認すること:**
1. `cwd` のパスが実際のクローン先と一致しているか
2. `command` のPythonパスが正しいか（`which python` で確認）
3. JSON形式が正しいか（カンマ、括弧の閉じ忘れなど）
4. 既に他のMCPサーバーを設定している場合は、カンマで区切る

**複数のMCPサーバーを設定する例:**
```json
{
  "mcpServers": {
    "other-server": {
      "command": "...",
      "args": ["..."]
    },
    "check36": {
      "command": "python3",
      "args": ["-m", "check36.server"],
      "cwd": "/Users/username/projects/check_36"
    }
  }
}
```

### 4. Claude Desktop を再起動

Claude Desktopアプリを完全に終了して、再起動してください。

### 5. 使用例

Claude に以下のように話しかけます：

```
今月の総労働時間が150.5時間、休日労働が8時間です。
15日働いて、今日含めて残り8日です。上限チェックしてください。
```

Claude が自動的に `assess_current_month_tool` を呼び出して結果を表示します。

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

## 開発

### プロジェクト構成

```
check_36/
├── src/check36/
│   ├── __init__.py
│   ├── server.py       # MCPサーバーエントリポイント
│   ├── models.py       # Pydanticモデル
│   ├── calculator.py   # コア計算ロジック
│   └── utils.py        # ユーティリティ関数
├── tests/
│   └── test_calculator.py
├── pyproject.toml
└── README.md
```

### コード品質チェック

```bash
# 型チェック
mypy src/check36

# リンター
ruff check src/check36

# フォーマット
ruff format src/check36
```
