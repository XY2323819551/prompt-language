from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WikipediaResult:
    """Wikipedia查询结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class WikipediaTool(BaseTool):
    """用于查询Wikipedia百科的工具类"""
    
    def __init__(self):
        """初始化Wikipedia查询工具"""
        self.tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
        super().__init__()

    def search(self, query: str) -> WikipediaResult:
        """
        在Wikipedia上搜索内容。

        Args:
            query (str): 搜索查询字符串

        Returns:
            WikipediaResult: 搜索结果数据类实例
        """
        try:
            logger.info(f"执行Wikipedia搜索: {query}")
            result = self.tool.run(query)
            return WikipediaResult(
                success=True,
                message="搜索成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return WikipediaResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def wikipedia_search(query: str) -> str:
    """
    在Wikipedia百科中搜索内容并返回结果。

    这个函数使用Wikipedia API搜索相关内容，并返回格式化的结果。搜索结果
    包含条目的摘要信息。

    Args:
        query (str): 搜索查询字符串，例如 "Python programming language" 或
            "Albert Einstein biography"

    Returns:
        str: 搜索结果字符串。如果搜索成功，将包含相关条目的信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = wikipedia_search("Python programming language")
        >>> print(result)
        Python is a high-level, general-purpose programming language...

    Note:
        - 不需要API密钥
        - 支持多语言搜索
        - 返回结果包含条目摘要
    """
    tool = WikipediaTool()
    result = tool.search(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    query = "Python programming language"
    print(f"Searching Wikipedia for: {query}")
    print("-" * 80)
    result = wikipedia_search(query)
    print(result)