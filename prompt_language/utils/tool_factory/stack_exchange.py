from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging
from langchain_community.utilities import StackExchangeAPIWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StackExchangeResult:
    """Stack Exchange搜索结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class StackExchangeTool(BaseTool):
    """用于在Stack Exchange网站搜索的工具类"""
    
    def __init__(self):
        """初始化Stack Exchange工具"""
        self.tool = StackExchangeAPIWrapper()
        super().__init__()
    
    def search(self, query: str) -> StackExchangeResult:
        """
        在Stack Exchange上搜索。

        Args:
            query (str): 搜索查询字符串

        Returns:
            StackExchangeResult: 搜索结果数据类实例
        """
        try:
            logger.info(f"执行Stack Exchange搜索: {query}")
            result = self.tool.run(query)
            return StackExchangeResult(
                success=True,
                message="搜索成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return StackExchangeResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def stack_exchange_search(query: str) -> str:
    """
    在Stack Exchange网站上搜索并返回结果。

    这个函数在Stack Exchange网站（包括Stack Overflow等）上搜索问题和答案，
    并返回最相关的结果。

    Args:
        query (str): 搜索查询字符串，例如 "How to create a list in python" 或
            "JavaScript async await explanation"

    Returns:
        str: 搜索结果字符串。如果搜索成功，将包含相关问答的信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = stack_exchange_search("How to create a list in python")
        >>> print(result)
        In Python, you can create a list using several methods...

    Note:
        - 需要Stack Exchange API密钥
        - 结果包含问题和最佳答案
        - 默认搜索所有Stack Exchange网站
    """
    tool = StackExchangeTool()
    result = tool.search(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    query = "How to create a list in python"
    print(f"Searching Stack Exchange for: {query}")
    print("-" * 80)
    result = stack_exchange_search(query)
    print(result)