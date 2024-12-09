from typing import Optional, List, Dict
from dataclasses import dataclass
import arxiv
from .base import BaseTool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArxivResult:
    """Arxiv搜索结果的数据类"""
    success: bool
    message: str
    papers: Optional[List[Dict]] = None

class ArxivTool(BaseTool):
    """用于搜索arXiv论文的工具类"""
    
    def __init__(self):
        """初始化ArxivTool"""
        self.client = arxiv.Client()
        super().__init__()

    def search_papers(self, query: str, max_results: int = 1) -> ArxivResult:
        """
        在arXiv上搜索论文。

        Args:
            query (str): 搜索查询字符串
            max_results (int): 返回结果的最大数量

        Returns:
            ArxivResult: 包含搜索结果的数据类实例
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )

            papers = []
            for result in self.client.results(search):
                paper = {
                    'title': result.title,
                    'authors': [str(author) for author in result.authors],
                    'summary': result.summary,
                    'published': result.published.strftime("%Y-%m-%d"),
                    'pdf_url': result.pdf_url,
                    'entry_id': result.entry_id
                }
                papers.append(paper)

            return ArxivResult(
                success=True,
                message="搜索成功完成",
                papers=papers
            )

        except Exception as e:
            return ArxivResult(
                success=False,
                message=f"搜索过程中出错: {str(e)}"
            )

def search_arxiv(query: str, max_results: int = 1) -> str:
    """
    在arXiv上搜索学术论文并返回格式化结果。

    这个函数使用arXiv API搜索学术论文，并返回格式化的结果字符串。每个论文条目包含标题、
    作者、发布日期、摘要等信息。

    Args:
        query (str): 搜索查询字符串，例如 "attention is all you need" 或 
            "Transformer architecture"
        max_results (int, optional): 要返回的最大结果数量。默认为1。

    Returns:
        str: 格式化的搜索结果字符串。如果搜索成功，将包含论文的详细信息；
            如果失败，将返回错误信息。

    Examples:
        >>> results = search_arxiv("attention is all you need")
        >>> print(results)
        1. Title: Attention Is All You Need
           Authors: Ashish Vaswani, Noam Shazeer, ...
           Published: 2017-06-12
           Summary: The dominant sequence transduction models...
           PDF URL: https://arxiv.org/pdf/1706.03762.pdf
           ArXiv ID: 1706.03762

    Note:
        - 返回结果按相关性排序
        - 每个论文条目包含完整的元数据信息
    """
    tool = ArxivTool()
    result = tool.search_papers(query, max_results)
    
    if not result.success:
        return result.message
        
    if not result.papers:
        return "未找到相关论文。"
        
    formatted_results = []
    for i, paper in enumerate(result.papers, 1):
        formatted_paper = (
            f"{i}. Title: {paper['title']}\n"
            f"   Authors: {', '.join(paper['authors'])}\n"
            f"   Published: {paper['published']}\n"
            f"   Summary: {paper['summary']}\n"
            f"   PDF URL: {paper['pdf_url']}\n"
            f"   ArXiv ID: {paper['entry_id']}\n"
        )
        formatted_results.append(formatted_paper)
        
    return "\n".join(formatted_results)

if __name__ == "__main__":
    # 测试代码
    query = "Transformer architecture"
    print(f"Searching arxiv for: {query}")
    print("-" * 80)
    results = search_arxiv(query)
    print(results)
    