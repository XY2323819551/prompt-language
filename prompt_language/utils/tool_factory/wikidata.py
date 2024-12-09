from typing import Optional
from dataclasses import dataclass
from .base import BaseTool
import logging
from langchain_community.tools.wikidata.tool import WikidataAPIWrapper, WikidataQueryRun

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WikidataResult:
    """Wikidata查询结果的数据类"""
    success: bool
    message: str
    content: Optional[str] = None

class WikidataTool(BaseTool):
    """用于查询Wikidata知识库的工具类"""
    
    def __init__(self):
        """初始化Wikidata查询工具"""
        self.tool = WikidataQueryRun(api_wrapper=WikidataAPIWrapper())
        super().__init__()

    def query(self, query: str) -> WikidataResult:
        """
        执行Wikidata查询。

        Args:
            query (str): 查询字符串

        Returns:
            WikidataResult: 查询结果数据类实例
        """
        try:
            logger.info(f"执行Wikidata查询: {query}")
            result = self.tool.run(query)
            return WikidataResult(
                success=True,
                message="查询成功完成",
                content=result
            )
        except Exception as e:
            logger.error(f"查询过程中出错: {str(e)}")
            return WikidataResult(
                success=False,
                message=f"查询过程中出错: {str(e)}"
            )

def wikidata_query(query: str) -> str:
    """
    在Wikidata知识库中执行查询并返回结果。

    这个函数使用Wikidata API执行查询，可以获取实体的属性、关系等信息。

    Args:
        query (str): 查询字符串，例如 "Alan Turing" 或 "Albert Einstein"。
            可以是实体名称或更复杂的查询语句。

    Returns:
        str: 查询结果字符串。如果查询成功，将包含相关实体的信息；
            如果失败，将返回错误信息。

    Examples:
        >>> result = wikidata_query("Alan Turing")
        >>> print(result)
        Alan Turing was a British mathematician and computer scientist...

    Note:
        - 不需要API密钥
        - 支持多语言查询
        - 返回结果的格式取决于查询的类型
    """
    tool = WikidataTool()
    result = tool.query(query)
    return result.content if result.success else result.message

if __name__ == "__main__":
    # 测试代码
    query = "Alan Turing"
    print(f"Querying Wikidata for: {query}")
    print("-" * 80)
    result = wikidata_query(query)
    print(result)
