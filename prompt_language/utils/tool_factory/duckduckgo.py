from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging
from langchain_community.tools import DuckDuckGoSearchResults, DuckDuckGoSearchRun

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DuckDuckGoResult:
    """DuckDuckGo搜索结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class DuckDuckGoSearchTool(BaseTool):
    """用于执行DuckDuckGo搜索的工具类"""
    
    def __init__(self, raw_results: bool = False, max_results: int = 4, backend: str = "text"):
        """
        初始化DuckDuckGo搜索工具。

        Args:
            raw_results (bool): 是否返回原始结果
            max_results (int): 最大结果数量
            backend (str): 搜索后端类型，可选值包括"text"和"news"
        """
        if raw_results:
            self.tool = DuckDuckGoSearchResults(max_results=max_results, backend=backend)
        else:
            self.tool = DuckDuckGoSearchRun()
        super().__init__()
    
    def search(self, query: str) -> DuckDuckGoResult:
        """
        执行DuckDuckGo搜索。

        Args:
            query (str): 搜索查询字符串

        Returns:
            DuckDuckGoResult: 搜索结果数据类实例
        """
        try:
            logger.info(f"执行DuckDuckGo搜索: {query}")
            result = self.tool.run(query)
            return DuckDuckGoResult(
                success=True,
                message="搜索成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return DuckDuckGoResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def duckduckgo_search(query: str, raw_results: bool = False, max_results: int = 4) -> str:
    """
    使用DuckDuckGo执行网络搜索并返回结果。

    这个函数使用DuckDuckGo搜索引擎执行搜索，并返回格式化的结果。可以选择返回
    原始结果或处理后的摘要信息。

    Args:
        query (str): 搜索查询字符串，例如 "Python programming tutorial" 或
            "latest AI developments"
        raw_results (bool, optional): 是否返回原始搜索结果。默认为False。
        max_results (int, optional): 返回的最大结果数量。默认为4。

    Returns:
        str: 搜索结果字符串。如果搜索成功，将包含相关网页的信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = duckduckgo_search("Python programming tutorial")
        >>> print(result)
        Python is a high-level programming language...

    Note:
        - 不需要API密钥
        - 支持文本和新闻两种搜索模式
        - 可以控制返回结果的数量
    """
    tool = DuckDuckGoSearchTool(raw_results=raw_results, max_results=max_results)
    result = tool.search(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    query = "What is the capital of France?"
    print("Testing raw search results:")
    print(duckduckgo_search(query, raw_results=True))
    print("\nTesting processed search results:")
    print(duckduckgo_search(query))
    
    