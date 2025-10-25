"""MCP Server entry point"""

from fastmcp import FastMCP

from .calculator import assess_current_month
from .models import SimpleAssessmentOutput, SimpleInput

# FastMCPインスタンス作成
mcp = FastMCP("check36-mcp-server")


@mcp.tool()
def assess_current_month_tool(
    totalWorkHoursToDate: float,
    holidayWorkHoursToDate: float,
    workingDaysElapsed: int | None = None,
    workingDaysRemaining: int | None = None,
    currentDate: str | None = None,
    autoCalculateWeekdays: bool = True,
) -> dict:
    """36協定の月次上限到達リスクを評価し、リカバリー策を提案

    Args:
        totalWorkHoursToDate: 前日までの総労働時間（時間）
        holidayWorkHoursToDate: 前日までの休日労働時間（時間）
        workingDaysElapsed: 前日までに働いた日数（省略時は自動計算）
        workingDaysRemaining: 今日を含む残りの稼働日数（省略時は自動計算）
        currentDate: 評価基準日（YYYY-MM-DD形式、省略時は今日）
        autoCalculateWeekdays: 土日を除外して自動計算するか（デフォルト: True）

    Returns:
        評価結果（45h上限・80h基準の評価とリカバリー提案）
    """
    # 入力モデル作成
    input_data = SimpleInput(
        totalWorkHoursToDate=totalWorkHoursToDate,
        holidayWorkHoursToDate=holidayWorkHoursToDate,
        workingDaysElapsed=workingDaysElapsed,
        workingDaysRemaining=workingDaysRemaining,
        currentDate=currentDate,
        autoCalculateWeekdays=autoCalculateWeekdays,
    )

    # 評価実行
    result: SimpleAssessmentOutput = assess_current_month(input_data)

    # 辞書に変換して返却
    return result.model_dump()


def main() -> None:
    """MCPサーバーを起動"""
    mcp.run()


if __name__ == "__main__":
    main()

