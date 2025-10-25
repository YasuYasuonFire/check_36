# 実装計画：36協定チェック MCP サーバー

## 前提
- Python FastMCP SDK を使用
- GitHub リポジトリとして管理（gh コマンド使用）
- 現在のディレクトリ `/Users/yasuyasu/hack/mcp/check_36` をリポジトリ化

## 技術スタック
- **言語**: Python 3.10+
- **MCP SDK**: FastMCP (Mastra.ai)
- **バリデーション**: Pydantic v2
- **パッケージ管理**: uv または pip
- **テスト**: pytest
- **型チェック**: mypy（任意）

## ディレクトリ構成（実装後）
```
check_36/
├── README.md                          # 更新: セットアップ・使用方法
├── IMPLEMENTATION_PLAN.md             # 本ファイル
├── pyproject.toml                     # 依存関係・プロジェクト設定
├── uv.lock / requirements.txt         # ロックファイル
├── .gitignore                         # Python/IDE除外設定
├── docs/
│   └── requirements/                  # 要件ドキュメント（既存）
├── schemas/                           # JSON Schema（既存）
├── templates/                         # 入力テンプレート（既存）
├── src/
│   └── check36/
│       ├── __init__.py
│       ├── server.py                  # MCP サーバーエントリポイント
│       ├── models.py                  # Pydantic モデル（入出力）
│       ├── calculator.py              # コア計算ロジック
│       └── utils.py                   # 日付・月日数計算等
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py             # 計算ロジックのテスト
│   ├── test_models.py                 # バリデーションテスト
│   └── fixtures/                      # テストデータ（OK/WARN/LIMIT）
└── scripts/
    └── run_mcp_inspector.sh           # MCP Inspector 起動スクリプト（任意）
```

## 実装ステップ

### 1. Git リポジトリ初期化とリモート作成
- `git init`
- `.gitignore` 作成（Python, IDE, venv 等）
- 初回コミット（要件ドキュメント・スキーマ）
- `gh repo create` でリモートリポジトリ作成・push

### 2. Python 環境セットアップ
- `pyproject.toml` 作成
  - プロジェクト名: `check36-mcp-server`
  - 依存: `fastmcp`, `pydantic>=2.0`, `python-dateutil`
  - dev依存: `pytest`, `mypy`, `ruff`
- `uv init` または `pip install -e .` で環境構築

### 3. プロジェクト構成作成
- `src/check36/` ディレクトリ作成
- `__init__.py` 配置
- `tests/` ディレクトリ作成

### 4. MCP サーバーエントリポイント実装
- `src/check36/server.py`
  - FastMCP インスタンス作成
  - サーバー起動関数 `main()`
  - `if __name__ == "__main__"` ブロック

### 5. 入力バリデーション実装
- `src/check36/models.py`
  - `SimpleInput` (Pydantic BaseModel)
    - `overtimeHoursToDate: float`
    - `holidayWorkHoursToDate: float`
    - `currentDate: Optional[str]`
    - `workingDaysRemaining: Optional[int]`
    - `config: Optional[ConfigModel]`
  - `LimitAssessment`, `SimpleAssessmentOutput` モデル
  - バリデーター（日付形式、非負値チェック）

### 6. コア計算ロジック実装
- `src/check36/calculator.py`
  - `calculate_month_info(current_date)`: 月日数・経過日数算出
  - `project_hours(hours_to_date, elapsed_days, total_days)`: 月末予測
  - `assess_limit(projected, limit, warn_ratio)`: リスクレベル判定
  - `calculate_recovery(projected, limit, avg_daily, remaining_days)`: リカバリ提案
  - `assess_current_month(input: SimpleInput) -> SimpleAssessmentOutput`: メイン関数

- `src/check36/utils.py`
  - `get_days_in_month(year, month)`: 月日数取得
  - `get_elapsed_days(year, month, day)`: 経過日数取得

### 7. MCP ツール実装
- `src/check36/server.py` にツール登録
  - `@mcp.tool()` デコレータで `assess_current_month` を公開
  - 入力: JSON → `SimpleInput` Pydantic モデル
  - 出力: `SimpleAssessmentOutput` → JSON

### 8. テストケース作成
- `tests/test_calculator.py`
  - OK パターン（時間外10h、余裕あり）
  - WARN パターン（時間外38h、80%接近）
  - LIMIT パターン（時間外50h、超過）
  - 境界値テスト（0h、45h丁度、80h丁度）
  - ゼロ割回避テスト
- `tests/fixtures/` にサンプル JSON 配置

### 9. README 更新
- セットアップ手順（uv/pip install）
- MCP サーバー起動方法
- Claude Desktop / MCP Inspector 連携設定例
- 使用例（入力 JSON サンプル、出力例）

### 10. 動作確認
- `pytest` でテスト実行
- MCP Inspector または Claude Desktop で実際に呼び出し
- 入力サンプル（`templates/simple_input.sample.json`）で動作確認

## 実装時の注意点
- **日付処理**: `currentDate` 未指定時はシステム日付（`datetime.now()`）を使用
- **ゼロ割回避**: 経過日数=0 または 残日数=0 の場合の処理
- **丸め**: 年休日数は `ceil()` で切り上げ、時間は小数第1位まで
- **80h基準**: 簡易単月評価として実装（将来は複数月平均へ拡張）
- **エラーハンドリング**: 不正な日付形式、負値入力時の適切なエラーメッセージ

## 次のステップ（実装後の拡張案）
- 複数月平均（2〜6か月）の80h評価
- 年間上限（360h/720h）の追跡
- 特別条項適用回数管理
- CSV入力対応
- グラフ出力（matplotlib）
- Slack/メール通知連携

## タイムライン（目安）
1. セットアップ（Git, Python環境）: 10分
2. 基本実装（モデル、計算ロジック、MCPツール）: 30分
3. テスト作成・実行: 20分
4. ドキュメント更新・動作確認: 15分

**合計**: 約75分

