from dotenv import load_dotenv
from langchain_community.utilities import SerpAPIWrapper
from .base import BaseTool
from typing import Optional, Dict
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@dataclass
class SearchResult:
    """搜索结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class SearchTool(BaseTool):
    """用于执行网络搜索的工具类"""
    
    def __init__(self, api_key: Optional[str] = None, params: Optional[Dict] = None):
        """
        初始化搜索工具。

        Args:
            api_key (str, optional): SerpAPI的API密钥
            params (Dict, optional): 搜索参数配置
        """
        self.search = SerpAPIWrapper(
            serpapi_api_key=api_key,
            params=params or {
                "engine": "google",
                "gl": "us",
                "hl": "zh-cn"
            }
        )
        super().__init__()

    def search_web(self, query: str) -> SearchResult:
        """
        执行网络搜索。

        Args:
            query (str): 搜索查询字符串

        Returns:
            SearchResult: 搜索结果数据类实例
        """
        try:
            logger.info(f"执行搜索查询: {query}")
            result = self.search.run(query)
            return SearchResult(
                success=True,
                message="搜索成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return SearchResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def serpapi_search(query: str) -> str:
    """
    使用SerpAPI执行网络搜索并返回结果。

    这个函数使用SerpAPI执行Google搜索，并返回格式化的搜索结果。搜索结果
    包含相关网页的摘要信息。

    Args:
        query (str): 搜索查询字符串，例如 "人工智能发展历史" 或 
            "Python编程教程"

    Returns:
        str: 搜索结果字符串。如果搜索成功，将包含相关网页的摘要信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = serpapi_search("什么是人工智能？")
        >>> print(result)
        人工智能（AI）是计算机科学的一个分支，致力于创建能够模拟人类智能的系统...

    Note:
        - 需要设置SERPAPI_API_KEY环境变量
        - 默认使用Google搜索引擎
        - 搜索结果默认使用中文
    """
    tool = SearchTool()
    result = tool.search_web(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试搜索
    print("Testing web search:")
    result = serpapi_search("什么是人工智能？")
    print(result) 