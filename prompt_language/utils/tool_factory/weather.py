import os
import json
from typing import Optional, Dict
from dataclasses import dataclass
from dotenv import load_dotenv
import logging
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_community.tools.openweathermap.tool import OpenWeatherMapQueryRun
from .base import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class WeatherResult:
    """天气查询结果的数据类"""
    success: bool
    message: str
    content: Optional[Dict] = None

class WeatherTool(BaseTool):
    """用于获取天气信息的工具类"""
    
    def __init__(self):
        """
        初始化天气查询工具。
        
        Raises:
            ValueError: 当环境变量OPENWEATHERMAP_API_KEY未设置时抛出
        """
        api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
        if not api_key:
            raise ValueError('OPENWEATHERMAP_API_KEY environment variable is not set')
        wrapper = OpenWeatherMapAPIWrapper()
        self.tool = OpenWeatherMapQueryRun(api_wrapper=wrapper)
        super().__init__()
    
    def get_weather(self, city: str) -> WeatherResult:
        """
        获取指定城市的天气信息。

        Args:
            city (str): 城市名称

        Returns:
            WeatherResult: 天气查询结果数据类实例
        """
        try:
            logger.info(f"获取城市天气信息: {city}")
            weather_info = self.tool.run(city)
            
            # 解析天气信息
            formatted_weather = {
                "status": weather_info.split("Detailed status: ")[1].split("\n")[0],
                "wind": {
                    "speed": float(weather_info.split("Wind speed: ")[1].split(" m/s")[0]),
                    "direction": int(weather_info.split("direction: ")[1].split("°")[0])
                },
                "humidity": int(weather_info.split("Humidity: ")[1].split("%")[0]),
                "temperature": {
                    "current": float(weather_info.split("Current: ")[1].split("°C")[0]),
                    "high": float(weather_info.split("High: ")[1].split("°C")[0]),
                    "low": float(weather_info.split("Low: ")[1].split("°C")[0]),
                    "feels_like": float(weather_info.split("Feels like: ")[1].split("°C")[0])
                },
                "cloud_cover": int(weather_info.split("Cloud cover: ")[1].split("%")[0])
            }
            
            # 添加降雨信息（如果有）
            rain_info = weather_info.split("Rain: ")[1].split("\n")[0]
            formatted_weather["rain"] = eval(rain_info) if rain_info != "{}" else {}
            
            return WeatherResult(
                success=True,
                message="天气信息获取成功",
                content=formatted_weather
            )
        except Exception as e:
            logger.error(f"获取天气信息时出错: {str(e)}")
            return WeatherResult(
                success=False,
                message=f"获取天气信息时出错: {str(e)}"
            )

def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。

    使用OpenWeatherMap API获取指定城市的当前天气信息，并返回格式化的JSON结果。

    Args:
        city (str): 需要查询天气的城市名称，使用英文表示，例如：London、Shanghai、
            Shenzhen。

    Returns:
        str: JSON格式的天气信息字符串，包含以下字段：
            - status (str): 天气状况描述
            - wind (dict): 风力信息
                - speed (float): 风速（米/秒）
                - direction (int): 风向（角度）
            - humidity (int): 湿度百分比
            - temperature (dict): 温度信息
                - current (float): 当前温度（摄氏度）
                - high (float): 最高温度（摄氏度）
                - low (float): 最低温度（摄氏度）
                - feels_like (float): 体感温度（摄氏度）
            - cloud_cover (int): 云量百分比
            - rain (dict): 降雨信息（如果有）

    Raises:
        ValueError: 当城市名称无效或API调用失败时抛出。

    Examples:
        >>> weather_info = get_weather('Shanghai')
        >>> print(weather_info)
        {
            "status": "晴",
            "wind": {"speed": 3.5, "direction": 180},
            "humidity": 65,
            "temperature": {
                "current": 25.6,
                "high": 28.0,
                "low": 22.0,
                "feels_like": 26.2
            },
            "cloud_cover": 10,
            "rain": {}
        }

    Note:
        - 需要设置OPENWEATHERMAP_API_KEY环境变量
        - 温度单位为摄氏度
        - 风速单位为米/秒
    """
    tool = WeatherTool()
    result = tool.get_weather(city)
    return json.dumps(result.content, ensure_ascii=False) if result.success else result.message

if __name__ == '__main__':
    # 测试代码
    print("Testing weather information:")
    print(get_weather('shanghai'))
