import datetime
import chinese_permanent_calendar as cpc
import calendar
from typing import Dict, Any

async def compute_calendar(date_str: str) -> Dict[str, Any]:
    """
    计算指定日期的农历和宜忌信息
    
    Args:
        date_str: 日期字符串，格式为 'YYYY-MM-DD'，如 '2024-03-20'
    
    Returns:
        Dict: 包含农历和宜忌信息的字典
    """
    try:
        # 解析日期字符串
        year, month, day = map(int, date_str.split('-'))
        
        # 检查日期是否有效
        if not (1 <= month <= 12 and 1 <= day <= calendar.monthrange(year, month)[1]):
            return {
                "success": False,
                "error": "无效的日期"
            }
        
        # 创建日期对象
        user_date = datetime.date(year, month, day)
        
        # 获取农历信息
        lunar_date = cpc.get_lunar_by_gregorian(user_date)
        
        return {
            "success": True,
            "gregorian_date": str(user_date),
            "lunar_date": str(lunar_date),
            "yi": lunar_date.Yi,
            "ji": lunar_date.Ji
        }
        
    except ValueError:
        return {
            "success": False,
            "error": "日期格式错误，请使用YYYY-MM-DD格式"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试用例
        test_dates = [
            "2024-03-20",  # 正常日期
            "2024-02-29",  # 闰年
            "2024-13-01",  # 无效月份
            "2024-04-31",  # 无效日期
            "invalid"      # 错误格式
        ]

        test_dates = [
            "2025-02-03"
        ]
        
        for date in test_dates:
            print(f"\n=========={date}==========\n")
            result = await compute_calendar(date)
            if result["success"]:
                print(f"公历: {result['gregorian_date']}")
                print(f"农历: {result['lunar_date']}")
                print(f"宜: {result['yi']}")
                print(f"忌: {result['ji']}")
            else:
                print(f"错误: {result['error']}")
    
    asyncio.run(test())

    