from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging
from langchain_community.tools import YouTubeSearchTool as Youtube

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class YouTubeResult:
    """YouTube搜索结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class YouTubeSearchTool(BaseTool):
    """用于搜索YouTube视频的工具类"""
    
    def __init__(self):
        """初始化YouTube搜索工具"""
        self.tool = Youtube()
        super().__init__()

    def search(self, query: str) -> YouTubeResult:
        """
        在YouTube上搜索视频。

        Args:
            query (str): 搜索查询字符串

        Returns:
            YouTubeResult: 搜索结果数据类实例
        """
        try:
            logger.info(f"执行YouTube搜索: {query}")
            result = self.tool.run(query)
            return YouTubeResult(
                success=True,
                message="搜索成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"搜索过程中出错: {str(e)}")
            return YouTubeResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def youtube_search(query: str) -> str:
    """
    在YouTube上搜索视频并返回结果。

    这个函数使用YouTube API搜索视频，并返回相关视频的信息，包括标题、
    链接、描述等。

    Args:
        query (str): 搜索查询字符串，例如 "Python tutorial" 或
            "Lex Fridman podcast"

    Returns:
        str: 搜索结果字符串。如果搜索成功，将包含相关视频的信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = youtube_search("Lex Fridman podcast")
        >>> print(result)
        1. Title: The Nature of Reality - Lex Fridman
           URL: https://youtube.com/watch?v=...
           Description: In this episode...

    Note:
        - 需要YouTube API密钥
        - 返回结果包含视频的基本信息
        - 可能受到YouTube API限制
    """
    tool = YouTubeSearchTool()
    result = tool.search(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    query = "Lex Fridman podcast"
    print(f"Searching YouTube for: {query}")
    print("-" * 80)
    result = youtube_search(query)
    print(result)